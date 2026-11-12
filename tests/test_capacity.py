def test_partial_day_absence(db):
    assert db.execute("SELECT scheduled_hours, absence_hours, available_hours FROM detail_daily_capacity WHERE employee_id='E104' AND work_date='2024-03-12'").fetchone() == (8, 4, 4)


def test_absence_capped_at_schedule(db):
    assert db.execute("SELECT absence_hours, available_hours FROM detail_daily_capacity WHERE employee_id='E102' AND work_date='2024-03-15'").fetchone() == (7.5, 0)


def test_daily_department_changes_on_effective_date(db):
    assert db.execute("SELECT department_id FROM detail_cap_daily_assignments WHERE employee_id='E104' AND work_date IN ('2024-03-14', '2024-03-15') ORDER BY work_date").fetchall() == [('D10',), ('D20',)]


def test_daily_grain(db):
    assert db.execute("SELECT employee_id, work_date FROM detail_daily_capacity GROUP BY 1, 2 HAVING count(*) <> 1").fetchall() == []


def test_weekends_excluded(db):
    assert db.execute("SELECT count(*) FROM detail_cap_calendar WHERE strftime('%w', work_date) IN ('0', '6')").fetchone()[0] == 0


def test_country_holiday_excluded(db):
    assert db.execute("SELECT count(*) FROM detail_daily_workforce WHERE employee_id='E102' AND work_date='2024-03-29'").fetchone()[0] == 0
    assert db.execute("SELECT count(*) FROM detail_daily_workforce WHERE employee_id='E101' AND work_date='2024-03-29'").fetchone()[0] == 1


def test_hours_balance(db):
    assert db.execute("SELECT count(*) FROM report_monthly_capacity WHERE scheduled_hours <> absence_hours + available_hours OR available_hours < 0").fetchone()[0] == 0


def test_daily_to_monthly_reconciliation(db):
    assert db.execute("SELECT sum(available_hours) FROM detail_daily_capacity").fetchone() == db.execute("SELECT sum(available_hours) FROM report_monthly_capacity").fetchone()
