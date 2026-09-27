---
name: Frontend Conventions
description: "Use when modifying the active CareerAI frontend, HTML templates, CSS, browser JavaScript, API-driven UI, accessibility behavior, responsive layouts, or client-side PDF and speech features."
applyTo: "templates/**/*.html, templates/static/**/*.css, templates/static/**/*.js"
---

# Frontend Conventions

- Treat `templates/index.html` and `templates/static/` as the active frontend. Do not modify the archived nested Vite prototype unless it is explicitly in scope.
- Preserve the existing vanilla HTML/CSS/JavaScript architecture, Tailwind CDN usage, PDF.js integration, Font Awesome icons, and API base URL conventions unless the request changes the architecture.
- Keep API paths and response shapes compatible with `career_app/urls.py` and the serializers/views that own them. URL-encode query parameters and handle non-2xx responses before rendering data.
- Render user-controlled or API-provided text safely. Prefer `textContent`, DOM node creation, or an explicit escaping helper; do not interpolate untrusted values into `innerHTML`, attributes, URLs, or executable script.
- Preserve loading, empty, error, disabled, and unauthorized states for every asynchronous action. Prevent duplicate submissions and restore controls in `finally` blocks.
- Use semantic HTML, associated labels, keyboard-accessible controls, visible focus states, meaningful button names, and appropriate live/status messaging for dynamic updates. Do not rely on color or hover alone to communicate state.
- Keep responsive layouts usable at narrow mobile widths and desktop widths. Avoid fixed dimensions that clip text, overlap controls, or prevent scrolling; test long labels, empty results, and large text.
- Keep visual changes consistent with the existing design tokens and page structure. Avoid unrelated rewrites, new frameworks, or dependency additions for a focused UI change.
- When changing client-side behavior, preserve authentication credentials, local storage semantics, PDF preview behavior, and graceful fallback behavior for unavailable speech recognition or external services.
- Validate the narrowest relevant slice first. Use `node --check templates/static/js/app.js` for JavaScript syntax when available, `git diff --check` for whitespace, and run `uv run python manage.py check` when template/API integration is affected. For browser-level testing, run `uv run manage.py runserver` and `uv run python -m http.server 3000 -d templates` in separate terminals, then open `http://127.0.0.1:3000`.
