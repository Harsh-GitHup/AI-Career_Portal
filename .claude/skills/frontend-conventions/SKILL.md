---
name: frontend-conventions
description: "Apply the AI Career Portal's frontend conventions when editing active HTML templates, CSS, browser JavaScript, API-driven UI, accessibility behavior, or responsive layouts."
---
# Frontend Conventions

- The active frontend is `templates/index.html` with assets under `templates/static/`; do not edit the nested Vite prototype unless explicitly requested.
- Preserve the vanilla HTML/CSS/JavaScript architecture, Tailwind CDN utilities, PDF.js, Font Awesome, API base URL, authentication credentials, and local storage behavior.
- Keep API routes and response shapes compatible with `career_app/urls.py`, views, and serializers. URL-encode query parameters and handle non-2xx responses before rendering.
- Render API and user text safely with `textContent` or DOM construction. Do not put untrusted data into `innerHTML`, attributes, URLs, or executable script without validation or escaping.
- Preserve loading, empty, error, disabled, unauthorized, and fallback states for asynchronous actions; restore controls in `finally` blocks.
- Use semantic HTML, associated labels, keyboard-accessible controls, visible focus states, meaningful button names, and status messaging. Do not rely on color or hover alone.
- Keep layouts usable on mobile and desktop, including long labels, empty results, large text, and scrolling content.
- Use `node --check templates/static/js/app.js`, `git diff --check`, and `uv run python manage.py check` when relevant. For browser-level testing, run `uv run manage.py runserver` and `uv run python -m http.server 3000 -d templates` in separate terminals, then open `http://127.0.0.1:3000`.
