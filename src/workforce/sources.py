"""Load CSV extracts using explicit source contracts."""

import csv
from datetime import date
import json
import math
from pathlib import Path
import sqlite3


def load_sources(connection: sqlite3.Connection, fixtures: Path) -> None:
    contracts = json.loads((fixtures / "contracts.json").read_text())
    for name, contract in contracts.items():
        columns = contract["columns"]
        definitions = ", ".join(
            f'"{column}" {"TEXT" if kind == "DATE" else kind}'
            for column, kind in columns.items()
        )
        connection.execute(f"CREATE TABLE raw_{name} ({definitions})")
        path = fixtures / contract["file"]
        with path.open(newline="") as source:
            reader = csv.reader(source)
            if next(reader, None) != list(columns):
                raise ValueError(f"{path}: header must match {list(columns)}")
            for line, row in enumerate(reader, start=2):
                if len(row) != len(columns):
                    raise ValueError(f"{path}:{line}: wrong number of columns")
                values = []
                for (column, kind), value in zip(columns.items(), row):
                    if not value:
                        values.append(None)
                        continue
                    try:
                        if kind == "DATE":
                            parsed = date.fromisoformat(value)
                            if parsed.isoformat() != value:
                                raise ValueError("expected YYYY-MM-DD")
                        elif kind == "REAL":
                            value = float(value)
                            if not math.isfinite(value):
                                raise ValueError("expected finite number")
                    except ValueError as exc:
                        raise ValueError(f"{path}:{line}: invalid {column}: {exc}") from exc
                    values.append(value)
                placeholders = ", ".join("?" for _ in values)
                connection.execute(f"INSERT INTO raw_{name} VALUES ({placeholders})", values)
        for column in contract["required"]:
            if connection.execute(f'SELECT 1 FROM raw_{name} WHERE "{column}" IS NULL').fetchone():
                raise ValueError(f"{name}.{column}: missing required values")
        keys = ", ".join(contract["key"])
        if connection.execute(f"SELECT {keys} FROM raw_{name} GROUP BY {keys} HAVING count(*) > 1").fetchone():
            raise ValueError(f"{name}: duplicate source key")
        for check in contract.get("checks", []):
            if connection.execute(f"SELECT 1 FROM raw_{name} WHERE NOT ({check})").fetchone():
                raise ValueError(f"{name}: rows violate {check}")
