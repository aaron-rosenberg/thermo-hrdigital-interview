# Workforce Warehouse

Your task is to resolve the two reported issues in [bugs/](bugs/). Use those tickets to guide your time.

People Analytics reports for headcount, recruiting, internal transfers, and workforce capacity. Python loads CSV extracts into one SQLite database and runs one SQL file per business area. All source records are synthetic; do not add personal data or credentials.

## Setup and build

Requires Python 3.11+ and uv. Pipeline runtime uses only Python standard-library modules, including `sqlite3`; no database server is needed. Tests use pytest, declared in the development dependency group. The build backend is setuptools.

From repository root:

```bash
uv run python run_this_first.py
```

This installs dependencies as needed and builds `.local/workforce.sqlite`. Every build replaces the entire warehouse. Failed builds preserve the previous output; source fixtures are never modified.

Custom source and output paths:

```bash
uv run workforce build --fixtures fixtures --output .local/comparison.sqlite
```

## Query

Raw extracts, intermediate details, and reports remain available under `raw_`, `detail_`, and `report_` table prefixes. Dates use ISO text; missing values use SQL null.

With SQLite CLI:

```bash
sqlite3 .local/workforce.sqlite '.tables'
sqlite3 -header -column .local/workforce.sqlite 'SELECT * FROM report_monthly_headcount ORDER BY snapshot_date, department_id;'
```

Or use Python's built-in SQLite interface:

```bash
uv run python -c "import sqlite3; db=sqlite3.connect('file:.local/workforce.sqlite?mode=ro', uri=True); print(db.execute('SELECT * FROM report_monthly_headcount ORDER BY snapshot_date, department_id').fetchall()); db.close()"
```

## Development

```bash
uv run pytest
```

Tests build isolated temporary databases. Generated outputs belong under `.local/` and must not be committed.

- `src/workforce/`: CSV loading, preparation, build sequence, and CLI.
- `src/workforce/sql/`: SQLite transformations and reports.
- `fixtures/`: synthetic extracts and machine-readable source contracts.
- `tests/`: metric and build checks.
- `bugs/`: reported issues.

See [source contracts](docs/sources.md) and [metric definitions](docs/metrics.md).
