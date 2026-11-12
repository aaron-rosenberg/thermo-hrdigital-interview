def test_department_funnel(db):
    assert db.execute("SELECT applications, screened, interviewed, offered, hired FROM report_recruiting_funnel WHERE department_id='D20'").fetchone() == (2, 2, 1, 1, 1)


def test_no_application_loss(db):
    assert db.execute("SELECT sum(applications) FROM report_recruiting_funnel").fetchone()[0] == 6


def test_rejected_application_has_no_hire(db):
    assert db.execute("SELECT hired_date FROM detail_application_progress WHERE application_id='A2'").fetchone()[0] is None


def test_progress_preserves_stage_dates(db):
    assert db.execute("SELECT screened_date, offered_date FROM detail_application_progress WHERE application_id='A1'").fetchone() == ('2024-01-08', '2024-02-01')


def test_source_conversion(db):
    assert db.execute("SELECT applications, hires FROM report_recruiting_sources WHERE source='referral'").fetchone() == (1, 1)


def test_non_hiring_source_retained(db):
    assert db.execute("SELECT applications, hires FROM report_recruiting_sources WHERE source='careers'").fetchone() == (2, 0)


def test_days_from_opening_to_first_hire(db):
    assert db.execute("SELECT days_to_fill FROM report_time_to_fill WHERE requisition_id='R1'").fetchone()[0] == 60
    rows = db.execute("SELECT requisition_id, days_to_fill FROM report_time_to_fill WHERE days_to_fill IS NOT NULL ORDER BY days_to_fill").fetchall()
    assert rows == [('R4', 20), ('R1', 60), ('R5', 100)]


def test_unfilled_requisition_has_null_duration(db):
    assert db.execute("SELECT days_to_fill FROM report_time_to_fill WHERE requisition_id='R2'").fetchone()[0] is None
