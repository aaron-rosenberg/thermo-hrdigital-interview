CREATE TABLE detail_hc_employees AS
SELECT employee_id, hire_date, termination_date, worker_type, country FROM raw_employees;

CREATE TABLE detail_hc_eligible_snapshots AS
SELECT s.snapshot_date, e.employee_id
FROM raw_snapshots s
JOIN detail_hc_employees e ON e.hire_date <= s.snapshot_date
    AND (e.termination_date IS NULL OR s.snapshot_date < e.termination_date)
WHERE e.worker_type = 'employee';

CREATE TABLE detail_headcount_employee_snapshots AS
SELECT e.snapshot_date, e.employee_id, a.department_id
FROM detail_hc_eligible_snapshots e
JOIN raw_assignments a ON a.employee_id = e.employee_id
    AND a.effective_start <= e.snapshot_date
    AND (a.effective_end IS NULL OR e.snapshot_date < a.effective_end);

CREATE TABLE report_monthly_headcount AS
SELECT e.snapshot_date, e.department_id, d.department_name, count(*) AS headcount
FROM detail_headcount_employee_snapshots e
JOIN raw_departments d USING (department_id)
GROUP BY e.snapshot_date, e.department_id, d.department_name;

CREATE TABLE report_headcount_totals AS
SELECT snapshot_date, sum(headcount) AS headcount
FROM report_monthly_headcount GROUP BY snapshot_date;
