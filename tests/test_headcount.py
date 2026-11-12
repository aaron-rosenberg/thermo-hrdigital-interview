def test_contingent_workers_excluded(db):
    assert db.execute("SELECT count(*) FROM detail_headcount_employee_snapshots WHERE employee_id='E105'").fetchone()[0] == 0


def test_hire_and_termination_boundaries(db):
    rows = db.execute("SELECT employee_id FROM detail_headcount_employee_snapshots WHERE snapshot_date='2024-03-31' ORDER BY employee_id").fetchall()
    assert rows == [('E101',), ('E102',), ('E103',), ('E104',), ('E106',), ('E108',)]
    assert db.execute("SELECT count(*) FROM detail_headcount_employee_snapshots WHERE employee_id='E103' AND snapshot_date='2024-04-30'").fetchone()[0] == 0


def test_one_row_per_employee_and_snapshot(db):
    assert db.execute("SELECT snapshot_date, employee_id FROM detail_headcount_employee_snapshots GROUP BY 1, 2 HAVING count(*) <> 1").fetchall() == []


def test_historical_assignment_is_effective_at_snapshot(db):
    assert db.execute("SELECT department_id FROM detail_headcount_employee_snapshots WHERE employee_id='E104' ORDER BY snapshot_date").fetchall() == [
        ('D10',), ('D10',), ('D30',), ('D10',)]


def test_monthly_totals(db):
    assert db.execute("SELECT headcount FROM report_headcount_totals ORDER BY snapshot_date").fetchall() == [(4,), (5,), (6,), (6,)]


def test_report_reconciles_to_eligible_population(db):
    actual = db.execute("SELECT snapshot_date, sum(headcount) FROM report_monthly_headcount GROUP BY snapshot_date ORDER BY snapshot_date").fetchall()
    expected = db.execute("SELECT snapshot_date, count(*) FROM detail_hc_eligible_snapshots GROUP BY snapshot_date ORDER BY snapshot_date").fetchall()
    assert actual == expected
