# AI Career Portal Agent Guide

## Active Project

- The active application is the root Django project: `career_app/`, `core_project/`, `templates/`, `manage.py`, and root configuration.
- `career-readiness-platform/` is archived/reference material. Do not modify it unless the request names it explicitly.
- Start with the smallest relevant module, view, task, adapter, template, or test. Preserve unrelated work-tree changes.
- Treat `.env`, credentials, uploaded media, databases, caches, and generated files as sensitive or local artifacts. Do not print secrets or commit them.

## Source Boundaries

- API routes are defined in [career_app/urls.py](career_app/urls.py); request behavior is primarily in [career_app/views.py](career_app/views.py).
- Domain models and persistence contracts are in [career_app/models.py](career_app/models.py); serializers are in [career_app/serializers.py](career_app/serializers.py).
- Resume analysis and offline fallback logic are in [career_app/ml_pipeline.py](career_app/ml_pipeline.py) and [career_app/local_nlp.py](career_app/local_nlp.py).
- Background scraping and match generation are in [career_app/tasks.py](career_app/tasks.py) and [career_app/adapters/](career_app/adapters/).
- The active frontend is [templates/index.html](templates/index.html) with assets under [templates/static/](templates/static/), not the nested Vite prototype.
- Use [README.md](README.md) for the full setup, API overview, environment variables, and architecture details. Link to it instead of duplicating those details here.

## Validation

From the repository root, use the project-managed environment when available:

```text
uv run python manage.py check
uv run manage.py test
uv run python -m compileall -q career_app core_project manage.py
uvx ruff format --check career_app core_project manage.py
uvx ruff check career_app core_project manage.py
```

Run the narrowest relevant check first. For a focused Django test, use `uv run manage.py test <target>`. Redis is needed for Celery workers, but ordinary API checks and tests should not require a running worker when tasks are mocked or unavailable.

## Change Rules

- When a request says "fix the attached problem" but no diagnostic, file, line, or error text is available, do not guess. Inspect available diagnostics first; if none are accessible, ask for the exact file, line, and message. Confirm the reported symbol or issue exists before editing.
- Fix confirmed root causes with the smallest compatible change; avoid speculative refactors and unnecessary migrations.
- Add or update a focused regression test for behavior that can be tested.
- Keep dependency changes separate from feature fixes. Inspect both `pyproject.toml`/`uv.lock` and `requirements.txt` before changing versions.
- Validate immediately after each substantive edit, then run the relevant broader check before finishing.
- Do not claim success when a check was unavailable or failed; report the exact command and result.
