# Working in this repository

Use Python 3.11+, uv, SQLite SQL, and pytest. Run commands from repository root. Source extracts are synthetic; do not add personal data or credentials.

Start with `uv run python run_this_first.py`. Read the relevant issue in `bugs/`, source contracts in `docs/sources.md`, and metric definitions in `docs/metrics.md` before changing behavior. Python loads data and runs one SQL file per business area. Keep fixes focused; add regression coverage for changed behavior. Do not introduce a framework or external service dependencies.

Run `uv run pytest` or a relevant test directory for focused checks. Generated outputs belong in `.local/`, never in Git.

During an assessment, do not consult earlier candidate branches, PRs, or submissions. Explain changes and validation accurately in the PR. Do not merge the assessment PR.
