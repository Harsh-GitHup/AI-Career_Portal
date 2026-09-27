---
name: frontend-update
description: "Update and validate the active CareerAI frontend in templates/ using vanilla HTML, CSS, and JavaScript. Use for UI changes, responsive fixes, accessibility, API-driven interactions, PDF preview, speech recognition, or frontend bug fixes."
argument-hint: "Describe the UI flow, page, component, or browser behavior to change"
user-invocable: true
---
# Frontend Update

## Scope

- The active frontend is `templates/index.html` with assets in `templates/static/`.
- The nested `career-readiness-platform/` Vite prototype is archived/reference material and is out of scope unless explicitly named.
- Preserve existing user changes and the current vanilla HTML/CSS/JavaScript architecture.

## Procedure

1. Identify the affected screen, DOM elements, event handlers, API endpoint, and existing CSS classes before editing.
2. Trace the API contract to `career_app/urls.py`, views, and serializers when the change reads or submits data.
3. State the expected behavior and one focused browser or syntax check that could disprove the implementation.
4. Make the smallest focused edit. Preserve loading, empty, error, disabled, unauthorized, and offline/fallback states.
5. Use semantic HTML and accessible labels, keyboard interaction, focus visibility, status messaging, and controls that remain usable on mobile and desktop.
6. Treat all API and user text as untrusted. Use `textContent` or DOM construction; escape values before unavoidable HTML interpolation and validate dynamic URLs.
7. Validate JavaScript with `node --check templates/static/js/app.js` when available, run `git diff --check`, and run `uv run python manage.py check` when templates or API integration are affected.
8. For browser-level testing, run `uv run manage.py runserver` and `uv run python -m http.server 3000 -d templates` in separate terminals from the repository root, then open `http://127.0.0.1:3000`. Exercise the affected flow and report checks that could not run.

## UI Rules

- Keep the existing visual language, CDN dependencies, and page structure unless the user explicitly requests a redesign.
- Avoid layout shifts, clipped text, overlapping controls, inaccessible icon-only buttons, and fixed heights that hide content.
- Do not add a framework or package for a localized frontend change.
- Keep authentication credentials, local storage behavior, PDF.js rendering, speech-recognition fallback, and API response handling intact unless intentionally changed.

## Output

Report the files changed, user-visible behavior, accessibility considerations, API impact, exact validation commands, and any remaining browser-only risks.
