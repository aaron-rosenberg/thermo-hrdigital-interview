# Source contracts

`fixtures/contracts.json` declares CSV filenames, ordered column names, logical types (TEXT, REAL, DATE; dates stored as ISO text), non-null fields, unique keys, and row-level checks. The loader rejects malformed headers, invalid types, missing required values, duplicate keys, and violated row checks before publishing output.

The source data guarantees valid foreign keys, nonoverlapping assignment history, and one applicable assignment per eligible employee/date. The loader validates individual extracts, not these cross-table guarantees.

## HRIS extracts

`employees.csv` has one row per employee, with hire/termination dates, worker category, and country. Worker categories include employees and contingent workers.

`assignments.csv` has one row per employee/effective-start pair. It contains department, effective interval, and movement reason. Initial rows use reason `hire`; subsequent department changes may use `internal_move`. A new assignment starts on the same date the previous assignment ends. Empty end means ongoing.

History is complete throughout the reporting window and does not overlap. A latest-assignment view represents the latest known assignment, not a general historical attribute. Source dates use `[start, end)` intervals. Source data may include assignments after a historical reporting date.

## Organization master

`departments.csv` contains unique department IDs, display names, and business units. Finance and People belong to Corporate; Operations belongs to Laboratory Services.

Department IDs are stable across assignment events. Every department referenced by the synthetic HRIS and recruiting extracts exists in this dimension. Names and business units are current labels; historical organization restructuring is not modeled.

Consumers group by department ID and enrich with display names. Employee names, manager identities, cost centers, and organizational hierarchy are deliberately absent: no pipeline needs them for its current metric.

## Reporting calendar

`snapshots.csv` declares four month-ends: January 31, February 29, March 31, and April 30, 2024. No report uses the machine's current date. Reporting dates are independent of the machine clock.

Headcount reports those exact snapshot dates. Capacity creates weekdays from the first day of the earliest snapshot month through the latest snapshot date. Recruiting and transfers report their event-derived periods, independent of the snapshot calendar.

`holidays.csv` supplies country-specific nonworking dates for capacity. Calendar dates have no timezone. February includes leap day. Snapshot contracts reject dates that are not month-end.

## Recruiting exports

`requisitions.csv`: one requisition, owning department, opening date, optional closing date. Closing a requisition alone does not establish a hire.

`applications.csv`: one application to one requisition, applied date, and acquisition source. One person could apply more than once in a real system; this dataset counts applications and has no applicant identity field.

`stage_events.csv`: at most one milestone per application/stage. Allowed stages: screen, interview, offer, hired, rejected. Events record reached milestones; rejection does not erase earlier progression. All application and requisition references are valid. This extract is already deduplicated upstream.

## Workforce operations extracts

`absences.csv`: unique absence ID, employee, date, hours, category. Categories are annual leave and sick; no health detail is stored. Multiple records on a day are summed. Capacity caps total absence at scheduled hours.

`work_schedules.csv`: one fixed daily schedule per employee. This synthetic model has no schedule history or part-week patterns. A UK schedule is 7.5 hours; US schedules are 8 hours.

`holidays.csv`: unique country/date pairs and a display label. Capacity excludes weekends and country holidays. Absences on excluded dates contribute no capacity reduction. Only dates during active employment count. Contingent workers do not enter the capacity population.
