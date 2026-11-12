"""Build the workforce warehouse. Run: uv run python run_this_first.py"""

from contextlib import closing
from pathlib import Path
import sqlite3

from workforce.runner import build


def main() -> None:
    root = Path(__file__).resolve().parent
    output = root / ".local/workforce.sqlite"
    build(root / "fixtures", output)
    with closing(sqlite3.connect(output)) as connection:
        reports = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'report_%' ORDER BY name"
        ).fetchall()
    print(f"Warehouse: {output}")
    print("Reports:\n" + "\n".join(f"  {name}" for (name,) in reports))
    print("Query: sqlite3 .local/workforce.sqlite 'SELECT * FROM report_monthly_headcount;'")
    print("Checks: uv run pytest")


if __name__ == "__main__":
    main()
