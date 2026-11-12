from contextlib import closing
import sqlite3

from workforce.runner import build


def test_transfer_direction(db):
    assert db.execute("SELECT employee_id, from_department_id, to_department_id FROM detail_transfer_events ORDER BY transfer_date").fetchall() == [
        ('E104', 'D10', 'D20'), ('E104', 'D20', 'D30'), ('E104', 'D30', 'D10')]


def test_adjacent_same_department_is_not_transfer(extracts, tmp_path):
    path = extracts / 'assignments.csv'
    path.write_text(path.read_text().replace('E101,D10,2023-06-01,,hire',
        'E101,D10,2023-06-01,2024-03-01,hire\nE101,D10,2024-03-01,,internal_move'))
    output = tmp_path / 'warehouse.sqlite'
    build(extracts, output)
    with closing(sqlite3.connect(output)) as connection:
        assert connection.execute("SELECT count(*) FROM detail_transfer_events WHERE employee_id='E101'").fetchone()[0] == 0


def test_transfer_month_end_and_route(db):
    assert db.execute("SELECT month_end, from_department_id, to_department_id, transfers FROM report_monthly_transfers ORDER BY 1, 2, 3").fetchall() == [
        ('2024-03-31', 'D10', 'D20', 1),
        ('2024-03-31', 'D20', 'D30', 1),
        ('2024-04-30', 'D30', 'D10', 1),
    ]


def test_tenure_measured_from_hire(db):
    assert db.execute("SELECT tenure_days FROM report_transfer_tenure WHERE employee_id='E104' AND transfer_date='2024-03-15'").fetchone()[0] == 196
