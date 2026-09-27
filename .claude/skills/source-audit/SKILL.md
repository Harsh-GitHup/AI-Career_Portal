---
name: source-audit
description: "Audit the active AI Career Portal source for bugs, errors, warnings, security risks, regressions, test gaps, maintainability issues, improvements, and upgrade opportunities. Use when reviewing or fixing Django backend and active static frontend code."
---
# Source Audit

## Scope

- Treat the root Django project (`career_app/`, `core_project/`, `templates/`, and `manage.py`) as active.
- Treat `career-readiness-platform/` as archived/reference material unless explicitly named.
- Ignore `.git/`, `.venv/`, caches, generated files, uploaded media, SQLite databases, and recovery copies unless directly relevant.
- Preserve existing user changes.

## Procedure

1. Define the requested scope and locate the smallest relevant file, symbol, failing behavior, or test.
2. Read the controlling implementation, nearby call sites, relevant models/serializers/settings, and existing tests only as needed.
3. State one falsifiable defect hypothesis and one focused check that could disprove it before editing.
4. Run the cheapest discriminating check first: focused test, Django check, syntax/type/lint check, build, or minimal reproduction.
5. Separate confirmed bugs, security findings, warnings, test gaps, maintainability issues, and recommendations. Do not present guesses as defects.
6. If remediation is requested, apply the smallest root-cause fix, add focused regression coverage when practical, and rerun the same check immediately.
7. Finish with findings ordered by severity, exact validation results, remaining risks, and prioritized improvements.

## Safety Rules

- Never expose or commit secrets from `.env`, credentials, API keys, uploaded files, or databases.
- Do not modify archived/reference code unless explicitly requested.
- Do not perform broad refactors or change public APIs, migrations, schemas, or unrelated behavior without evidence.
- If a request says "fix the attached problem" but no diagnostic, file, line, or error text is available, inspect available diagnostics first. If none are accessible, ask for the exact file, line, and message. Confirm the reported symbol or issue exists before editing.
- Do not claim a fix until a focused validation passes. Report unavailable or failing checks honestly.

## Validation Defaults

- Prefer `uv run python manage.py check` for backend configuration checks.
- Use `uv run manage.py test <target>` for focused Django tests.
- Use `uv run python -m compileall -q career_app core_project manage.py` for Python syntax validation.
- Use existing Ruff configuration for formatting and linting; do not introduce new tooling solely for an audit.
- Validate active frontend changes in `templates/` with the project’s available checks. Include the nested Vite prototype only when explicitly in scope.

## Output Format

### Findings

For each finding, provide severity, category, file and line, impact, evidence/root cause, and recommended or applied fix.

### Validation

List exact commands or checks and mark each passed, failed, or unavailable.

### Improvements and Upgrades

List recommendations separately from confirmed defects, with benefit, compatibility risk, and next step.

### Remaining Questions

Mention only assumptions, blocked checks, or decisions requiring user input.
