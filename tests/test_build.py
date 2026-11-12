from contextlib import closing
from pathlib import Path
import shutil
import sqlite3

import pytest

from workforce.cli import main
from workforce.runner import build
import workforce.runner as runner


def test_sql_failure_preserves_existing_database(extracts, tmp_path, monkeypatch):
    output = tmp_path / 'warehouse.sqlite'
    runner.build(extracts, output)
    before = output.read_bytes()
    sql = Path(shutil.copytree(runner.SQL, tmp_path / 'sql'))
    (sql / 'headcount.sql').write_text('SELECT invalid_column FROM raw_employees;')
    monkeypatch.setattr(runner, 'SQL', sql)
    with pytest.raises(ValueError, match='headcount.sql'):
        runner.build(extracts, output)
    assert output.read_bytes() == before
    assert not list(tmp_path.glob('workforce-*'))


def test_invalid_source_preserves_existing_database(extracts, tmp_path):
    output = tmp_path / 'warehouse.sqlite'
    runner.build(extracts, output)
    before = output.read_bytes()
    with (extracts / 'absences.csv').open('a') as source:
        source.write('X,E104,2024-03-12,not-hours,sick\n')
    with pytest.raises(ValueError, match='invalid hours'):
        runner.build(extracts, output)
    assert output.read_bytes() == before
    assert not list(tmp_path.glob('workforce-*'))


def test_cli_reports_missing_input(tmp_path, monkeypatch, caplog):
    monkeypatch.setattr('sys.argv', ['workforce', 'build', '--fixtures', str(tmp_path / 'missing'), '--output', str(tmp_path / 'out.sqlite')])
    assert main() == 1
    assert 'Build failed' in caplog.text


@pytest.mark.parametrize(('row', 'message'), [
    ('E101,2023-06-01,,employee,US', 'duplicate source key'),
    ('E999,2024-01-01,,unknown,US', 'violate'),
    (',2024-01-01,,employee,US', 'missing required'),
    ('E999,not-a-date,,employee,US', 'invalid hire_date'),
    ('E999,2024-02-01,2024-01-01,employee,US', 'violate'),
])
def test_invalid_source_records_rejected(extracts, tmp_path, row, message):
    with (extracts / 'employees.csv').open('a') as source:
        source.write(row + '\n')
    with pytest.raises(ValueError, match=message):
        build(extracts, tmp_path / 'output.sqlite')


def test_unexpected_header_rejected(extracts, tmp_path):
    path = extracts / 'employees.csv'
    path.write_text(path.read_text().replace('employee_id', 'person_id', 1))
    with pytest.raises(ValueError, match='header must match'):
        build(extracts, tmp_path / 'output.sqlite')


def test_rebuild_replaces_prior_contents(extracts, tmp_path):
    output = tmp_path / 'warehouse.sqlite'
    build(extracts, output)
    with closing(sqlite3.connect(output)) as db:
        before = db.execute('SELECT * FROM report_monthly_headcount ORDER BY 1, 2').fetchall()
        db.execute('CREATE TABLE scratch AS SELECT 1 AS value')
    build(extracts, output)
    with closing(sqlite3.connect(output)) as db:
        assert db.execute('SELECT * FROM report_monthly_headcount ORDER BY 1, 2').fetchall() == before
        assert db.execute("SELECT count(*) FROM sqlite_master WHERE name='scratch'").fetchone()[0] == 0
        for table in ('report_recruiting_funnel', 'report_monthly_transfers', 'report_monthly_capacity'):
            assert db.execute(f'SELECT count(*) FROM {table}').fetchone()[0] > 0
