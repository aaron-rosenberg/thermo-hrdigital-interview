CREATE TABLE detail_rec_requisitions AS
SELECT requisition_id, department_id, opened_date, closed_date FROM raw_requisitions;

CREATE TABLE detail_rec_applications AS
SELECT application_id, requisition_id, applied_date, source FROM raw_applications;

CREATE TABLE detail_application_progress AS
SELECT a.application_id, a.requisition_id, a.applied_date, a.source,
    min(e.event_date) FILTER (WHERE stage = 'screen') AS screened_date,
    min(e.event_date) FILTER (WHERE stage = 'interview') AS interviewed_date,
    min(e.event_date) FILTER (WHERE stage = 'offer') AS offered_date,
    min(e.event_date) FILTER (WHERE stage = 'hired') AS hired_date
FROM detail_rec_applications a LEFT JOIN raw_stage_events e USING (application_id)
GROUP BY a.application_id, a.requisition_id, a.applied_date, a.source;

CREATE TABLE report_recruiting_funnel AS
SELECT r.department_id, count(*) AS applications,
    count(p.screened_date) AS screened, count(p.interviewed_date) AS interviewed,
    count(p.offered_date) AS offered, count(p.hired_date) AS hired
FROM detail_application_progress p
JOIN detail_rec_requisitions r USING (requisition_id)
GROUP BY r.department_id;

CREATE TABLE report_time_to_fill AS
SELECT requisition_id, department_id, first_hired_date, days_to_fill
FROM detail_recruiting_durations;

CREATE TABLE report_recruiting_sources AS
SELECT source, count(*) AS applications, count(hired_date) AS hires
FROM detail_application_progress GROUP BY source;
