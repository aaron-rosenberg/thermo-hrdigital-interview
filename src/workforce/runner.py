"""Build one local SQLite warehouse from synthetic extracts."""

from datetime import date
import logging
import os
from pathlib import Path
import sqlite3
import tempfile

from workforce.sources import load_sources

SQL = Path(__file__).parent / "sql"
LOG = logging.getLogger(__name__)


def prepare_recruiting(connection: sqlite3.Connection) -> None:
    """Calculate calendar-day durations for requisitions, including unfilled ones."""
    connection.execute("""CREATE TABLE detail_recruiting_durations (
        requisition_id TEXT, department_id TEXT, first_hired_date TEXT,
        days_to_fill TEXT
    )""")
    requisitions = connection.execute("""
        SELECT r.requisition_id, r.department_id, r.opened_date, min(e.event_date)
        FROM raw_requisitions r
        LEFT JOIN raw_applications a USING (requisition_id)
        LEFT JOIN raw_stage_events e ON e.application_id = a.application_id AND e.stage = 'hired'
        GROUP BY r.requisition_id, r.department_id, r.opened_date
    """).fetchall()
    for requisition, department, opened, hired in requisitions:
        duration = str((date.fromisoformat(hired) - date.fromisoformat(opened)).days) if hired else None
        connection.execute("INSERT INTO detail_recruiting_durations VALUES (?, ?, ?, ?)",
                           (requisition, department, hired, duration))


def build(fixtures: Path, output: Path) -> None:
    """Rebuild all reports; preserve previous output if loading or SQL fails."""
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="workforce-", dir=output.parent) as directory:
        temporary = Path(directory) / "build.sqlite"
        connection = sqlite3.connect(temporary)
        try:
            load_sources(connection, fixtures)
            prepare_recruiting(connection)
            for filename in ("headcount.sql", "recruiting.sql", "transfers.sql", "capacity.sql"):
                try:
                    connection.executescript((SQL / filename).read_text())
                except sqlite3.Error as exc:
                    raise ValueError(f"{filename}: {exc}") from exc
            connection.commit()
        except sqlite3.Error as exc:
            raise ValueError(f"Source load failed: {exc}") from exc
        finally:
            connection.close()
        os.replace(temporary, output)
    LOG.info("Built %s", output)
