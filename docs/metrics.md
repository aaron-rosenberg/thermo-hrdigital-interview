# Metric definitions

Business definitions for the workforce reports. Counts are not full-time equivalents.

## Monthly headcount

An employee counts on snapshot date when hire date is on or before the snapshot and termination date is null or after the snapshot. Only `worker_type = employee` counts.

Business grain is one eligible employee per snapshot date. Department is the assignment effective on that snapshot date: effective start inclusive, effective end exclusive, null end ongoing. A hire on snapshot date counts; a termination on snapshot date does not. Reports aggregate to snapshot date / department ID, with current department display names.

`detail_headcount_employee_snapshots` supports reconciliation; `report_monthly_headcount` is the department report; `report_headcount_totals` is the monthly company total. Department changes must not change company totals or create duplicate employee snapshots.

## Recruiting metrics

The department funnel counts applications and how many reached screen, interview, offer, and hire milestones. It is lifetime progression for the committed extract, not a monthly cohort or current-stage distribution.

Time-to-fill is calendar days from requisition opening to first hired milestone. Unfilled requisitions remain present with null first-hire date and duration; zero is a real same-day fill, not a missing value. Source conversion counts applications and hires by acquisition source.

Output grains: one department for funnel; one requisition for time-to-fill; one source for source conversion. Multiple stage rows must not multiply applications in any report.

## Internal transfers

A transfer is a change between distinct consecutive departments in an employee's ordered assignment history. Initial assignment is not a transfer. Adjacent assignments in the same department do not count, regardless of movement reason.

Transfer date is the new assignment's effective start. Monthly flow groups by transfer month-end, source department, and destination department. Detail retains employee ID, reason, and department names. Tenure at transfer is calendar days from hire to transfer date.

## Workforce capacity

Create eligible employee weekdays across the reporting calendar. Exclude country holidays and contingent workers. Employment and assignment intervals use inclusive starts and exclusive ends.

For each employee/day, obtain the fixed work schedule and department effective that day. Sum absence records, cap at scheduled hours, and subtract to get available hours. Group daily facts into month-end / department reports.

Scheduled hours equal absence hours plus available hours. Department movement can split one employee's monthly hours across departments. This daily-hours metric is distinct from month-end employee headcount.
