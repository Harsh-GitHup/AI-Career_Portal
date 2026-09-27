---
name: django-conventions
description: "Apply the AI Career Portal's Django conventions when modifying views, URLs, serializers, models, migrations, Celery tasks, resume uploads, authentication, or active templates and frontend scripts."
---
# Django Conventions

- Keep routing in `career_app/urls.py` and request behavior in views, viewsets, serializers, and existing service boundaries. Do not place business logic in URL configuration or templates.
- Scope authenticated querysets by `request.user` at the database level. Never trust client-supplied user IDs, profile IDs, opportunity IDs, or ownership fields for authorization.
- Validate uploaded files for expected type, size, and parseability before expensive AI or persistence work. Never return raw exception details, provider responses, API keys, or uploaded file contents.
- Use Django ORM relationships and `transaction.atomic()` for multi-step writes that must remain consistent. Use `select_related()` or `prefetch_related()` to avoid N+1 queries when serializing collections.
- Treat model and serializer changes as API contract changes. Add migrations for model changes, inspect generated migrations, and add focused API/model tests before changing response shapes.
- Keep external API calls, scraping, AI inference, and Celery scheduling outside request-critical code when an existing task boundary supports it. Make retries bounded and tasks idempotent; log identifiers and useful context without secrets.
- Preserve the existing session-authentication and CORS behavior unless the security model is intentionally changing. Review CSRF, cookie, origin, and production `DEBUG` settings together.
- Use the project timezone and timezone-aware Django utilities for persisted timestamps, deadlines, and Celery schedules.
- Keep active frontend behavior compatible with contracts in `career_app/urls.py` and `career_app/serializers.py`. Safely render user/API text and do not interpolate untrusted values into executable HTML.
- Prefer focused tests in `career_app/tests.py` or the existing test layout. Mock network, AI providers, Redis, and scraping at their boundaries.
- Run the narrowest relevant check after edits, then run `uv run python manage.py check` and the relevant Django test target. Run migration checks when models or migrations change.
