CREATE TABLE detail_cap_calendar AS
WITH RECURSIVE calendar(work_date) AS (
    SELECT date(min(snapshot_date), 'start of month') FROM raw_snapshots
    UNION ALL
    SELECT date(work_date, '+1 day') FROM calendar
    WHERE work_date < (SELECT max(snapshot_date) FROM raw_snapshots)
)
SELECT work_date FROM calendar
WHERE strftime('%w', work_date) BETWEEN '1' AND '5';

CREATE TABLE detail_daily_workforce AS
SELECT c.work_date, e.employee_id, e.country, w.daily_hours
FROM detail_cap_calendar c
JOIN raw_employees e ON e.hire_date <= c.work_date
    AND (e.termination_date IS NULL OR c.work_date < e.termination_date)
JOIN raw_work_schedules w USING (employee_id)
WHERE e.worker_type = 'employee'
    AND NOT EXISTS (SELECT 1 FROM raw_holidays h
                    WHERE h.country = e.country AND h.holiday_date = c.work_date);

CREATE TABLE detail_cap_daily_assignments AS
SELECT w.work_date, w.employee_id, a.department_id, w.daily_hours
FROM detail_daily_workforce w
JOIN raw_assignments a ON a.employee_id = w.employee_id
    AND a.effective_start <= w.work_date
    AND (a.effective_end IS NULL OR w.work_date < a.effective_end);

CREATE TABLE detail_cap_absence_daily AS
SELECT employee_id, absence_date, sum(hours) AS absence_hours
FROM raw_absences GROUP BY employee_id, absence_date;

CREATE TABLE detail_daily_capacity AS
SELECT w.work_date, w.employee_id, w.department_id, w.daily_hours AS scheduled_hours,
    min(w.daily_hours, coalesce(a.absence_hours, 0)) AS absence_hours,
    w.daily_hours - min(w.daily_hours, coalesce(a.absence_hours, 0)) AS available_hours
FROM detail_cap_daily_assignments w
LEFT JOIN detail_cap_absence_daily a ON a.employee_id = w.employee_id AND a.absence_date = w.work_date;

CREATE TABLE report_monthly_capacity AS
SELECT date(work_date, 'start of month', '+1 month', '-1 day') AS month_end, department_id,
    sum(scheduled_hours) AS scheduled_hours, sum(absence_hours) AS absence_hours,
    sum(available_hours) AS available_hours
FROM detail_daily_capacity GROUP BY month_end, department_id;
