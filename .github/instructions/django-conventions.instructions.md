---
name: Django Conventions
description: "Use when modifying the active Django backend, REST API, models, migrations, Celery tasks, resume uploads, or Django-served templates and frontend scripts."
applyTo: "career_app/**/*.py, core_project/**/*.py, manage.py, templates/**/*.html, templates/static/**/*.js"
---

# Django Conventions

- Keep request routing in `career_app/urls.py` and request behavior in views, viewsets, serializers, and services that already own that responsibility. Do not add business logic to URL configuration or templates.
- Scope authenticated querysets by `request.user` at the database level. Do not trust client-supplied `user_id`, profile IDs, opportunity IDs, or ownership fields to authorize access.
- Validate uploaded files for expected type, size, and parseability before expensive AI or persistence work. Never expose raw exception details, provider responses, API keys, or uploaded file contents in API responses or logs.
- Use Django ORM relationships and `transaction.atomic()` for multi-step writes that must remain consistent. Avoid N+1 queries with `select_related()` or `prefetch_related()` when serializing collections.
- Treat model and serializer changes as contract changes. Add a migration for model changes, inspect the generated migration, and add focused API/model coverage before changing existing response shapes.
- Keep external API calls, scraping, AI inference, and Celery scheduling outside request-critical code when an existing task boundary supports it. Make task retries bounded and idempotent; log failures with identifiers and useful context, not secrets.
- Preserve the existing session-authentication and CORS behavior unless the request explicitly changes the security model. Review CSRF, cookie, origin, and production `DEBUG` settings together when changing authentication or cross-origin behavior.
- Use the project timezone and timezone-aware Django utilities for persisted timestamps, deadlines, and Celery schedules. Do not introduce naive datetimes.
- Keep active frontend behavior compatible with the API contracts in `career_app/urls.py` and `career_app/serializers.py`. Escape or safely render user/API text in browser DOM updates; do not interpolate untrusted values into executable HTML without sanitization.
- Prefer focused tests in `career_app/tests.py` or the existing test layout. Mock network, AI providers, Redis, and scraping at their boundaries so tests remain deterministic.
- Run the narrowest relevant check after edits, then use `uv run python manage.py check` and the relevant Django test target. Run migration checks when models or migrations change.
