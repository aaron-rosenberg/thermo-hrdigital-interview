CREATE TABLE detail_tr_assignment_history AS
SELECT employee_id, department_id, effective_start, effective_end, transfer_reason
FROM raw_assignments;

CREATE TABLE detail_assignment_changes AS
SELECT *, lag(department_id) OVER (PARTITION BY employee_id ORDER BY effective_start) AS previous_department_id
FROM detail_tr_assignment_history;

CREATE TABLE detail_transfer_events AS
SELECT employee_id, effective_start AS transfer_date,
    previous_department_id AS from_department_id, department_id AS to_department_id, transfer_reason
FROM detail_assignment_changes
WHERE previous_department_id IS NOT NULL AND previous_department_id <> department_id;

CREATE TABLE report_transfer_details AS
SELECT t.*, f.department_name AS from_department, d.department_name AS to_department
FROM detail_transfer_events t
JOIN raw_departments f ON f.department_id = t.from_department_id
JOIN raw_departments d ON d.department_id = t.to_department_id;

CREATE TABLE report_monthly_transfers AS
SELECT date(transfer_date, 'start of month', '+1 month', '-1 day') AS month_end, from_department_id, to_department_id,
    count(*) AS transfers
FROM report_transfer_details GROUP BY month_end, from_department_id, to_department_id;

CREATE TABLE report_transfer_tenure AS
SELECT t.employee_id, t.transfer_date, CAST(julianday(t.transfer_date) - julianday(e.hire_date) AS INTEGER) AS tenure_days
FROM detail_transfer_events t JOIN raw_employees e USING (employee_id);

CREATE TABLE report_monthly_mobility AS
SELECT date(transfer_date, 'start of month', '+1 month', '-1 day') AS month_end,
    count(*) AS employees_with_department_changes
FROM detail_transfer_events
GROUP BY month_end;
