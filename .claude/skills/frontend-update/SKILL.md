---
name: frontend-update
description: "Update and validate the active CareerAI frontend in templates/ using vanilla HTML, CSS, and JavaScript. Use for UI changes, responsive fixes, accessibility, API-driven interactions, PDF preview, speech recognition, or frontend bug fixes."
---
# Frontend Update

## Scope

- Work on `templates/index.html` and `templates/static/` for the active frontend.
- Treat `career-readiness-platform/` as archived/reference material unless explicitly named.
- Preserve user changes and the existing vanilla HTML/CSS/JavaScript architecture.

## Workflow

1. Locate the affected screen, DOM elements, event handlers, API endpoint, and CSS before editing.
2. Trace API changes to `career_app/urls.py`, views, and serializers.
3. State expected behavior and a focused check that could disprove the change.
4. Make the smallest focused edit while preserving loading, empty, error, disabled, unauthorized, and fallback states.
5. Use semantic HTML, labels, keyboard interaction, focus visibility, status messaging, and responsive layouts.
6. Treat API and user text as untrusted. Prefer `textContent` or DOM construction; escape unavoidable HTML interpolation and validate dynamic URLs.
7. Run `node --check templates/static/js/app.js` when available, `git diff --check`, and `uv run python manage.py check` when templates/API integration is affected.
8. For browser-level testing, run `uv run manage.py runserver` and `uv run python -m http.server 3000 -d templates` in separate terminals from the repository root, then open `http://127.0.0.1:3000`. Exercise the affected flow and report unavailable checks.

## Constraints

- Preserve existing visual language, CDN dependencies, authentication credentials, local storage behavior, PDF.js rendering, speech-recognition fallback, and API response handling unless intentionally changed.
- Do not add a framework or package for a localized UI change.
- Avoid clipped text, overlapping controls, inaccessible icon-only buttons, layout shifts, and fixed heights that hide content.

## Output

Report changed files, user-visible behavior, accessibility considerations, API impact, exact validation commands, and remaining browser-only risks.
