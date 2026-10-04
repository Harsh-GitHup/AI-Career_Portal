# 🚀 CareerAI - AI Career Portal

CareerAI is a Django and Django REST Framework application for resume analysis, career readiness, opportunity discovery, interview preparation, and personalized career guidance.

This document is the updated project guide for the active root application. The active application consists of the Django backend in `career_app/` and `core_project/`, plus the vanilla HTML/CSS/JavaScript frontend in `templates/`.

> `career-readiness-platform/` is archived/reference material and is not the frontend launched by the root Django project.

## ✨ What's New

The current project includes the following advanced architecture and security updates:

- **Fully Decoupled API (React-Ready):** Completely uncoupled backend architecture. Features custom `CsrfExemptSessionAuthentication` and robust CORS mapping (`CORS_ALLOW_CREDENTIALS`), allowing seamless integration with standalone frontends (like React/Next.js).
- **Production Security Hardening:** Strict dynamic toggling for HTTPS redirects (`SECURE_SSL_REDIRECT`), HTTP Strict Transport Security (`SECURE_HSTS_SECONDS`), and Secure/HttpOnly session cookies when deploying (`DEBUG=False`).
- **Hybrid Local NLP Engine:** Advanced offline fallback combining strict Regex validation, SpaCy Named Entity Recognition (`en_core_web_sm`) for name extraction, and a Triple-Failsafe for role matching (Hardcoded Rules -> HuggingFace Zero-Shot -> `sentence_transformers` Cosine Similarity) without bloating memory with Sklearn dependencies.
- **Persistent AI Interview Feedback:** Mock interview answers evaluated by Gemini (or local NLP) are now durably persisted across both the `StudentProfile` and the historical `ResumeAnalysis` records via JSONFields.
- **Isolated Dashboard UI State:** Advanced frontend session management in Vanilla JS ensures the main dashboard only populates during an active session, keeping historical data strictly compartmentalized in the "Analysis History" tab.
- **Hybrid Mock Interview Input:** Integrated a dual-mode response system. Candidates can utilize the browser's Web Speech API to dictate their answers, type them out manually via an always-visible textarea, or dictate and dynamically edit the transcript before submitting for AI evaluation.
- **Rate-Limiting & Asynchronous Offloading:** Heavy LLM extractions and web scraping are strictly delegated to Celery/Redis background workers to guarantee zero UI blocking and protect against API rate limits.

## 🌟 Main Features

### 📄 Resume intelligence

- Upload a PDF resume through the frontend or `POST /api/upload-resume/`.
- Use Gemini when `GOOGLE_API_KEY` is configured.
- Fall back to local processing when Gemini is unavailable, rate-limited, or not configured.
- Extract candidate name, summary, target professions, skills, skill gaps, projects, experience, academic records, resume improvements, and interview questions.
- Calculate a readiness score from the detected skill gaps and store the latest profile state.
- Preserve authenticated analyses in resume history.

### 🌐 Opportunity hub

- Display jobs, internships, courses, government schemes, fellowships, and other normalized opportunities.
- Filter opportunities by search text, opportunity type, and free/paid status.
- Deduplicate normalized records using a SHA-256 URL hash.
- Run external scraping and matching asynchronously through Celery.
- Show ranked profile matches with matching skills and reasoning.
- Bookmark matches and generate a role-specific cover letter for a selected opportunity.

### 🎤 Interview preparation

- Generate resume-specific technical and behavioral questions.
- Record answers with browser speech recognition when supported.
- Submit answers for Gemini evaluation or the local evaluator.
- Store interview feedback against a resume analysis when an analysis ID is supplied.

### 🤖 Career assistant

- Provide authenticated chatbot conversations.
- Include profile context and top opportunity matches in Gemini prompts.
- Use a lightweight local response engine for common resume, interview, learning, and job questions when the external model is unavailable.

### 🎨 Frontend experience

- Static dashboard interface served from `templates/index.html`.
- Dashboard, AI resume builder, mock interview, opportunity hub, saved matches, and analysis history views.
- PDF.js resume preview rendered onto canvases rather than an iframe.
- English/Hindi language controls using Google Translate integration.
- Tailwind CDN utilities, Font Awesome icons, and project CSS in `templates/static/css/style.css`.
- Browser JavaScript behavior in `templates/static/js/app.js`.

## 🏗️ Architecture

```text
Browser
  |
  | static HTML/CSS/JavaScript
  v
Django REST API (/api/)
  |
  +-- Authentication and session cookies
  +-- Resume analysis orchestration
  +-- Local NLP fallback
  +-- Gemini/LangChain integrations
  +-- Opportunity and recommendation queries
  +-- Cover letters, interview evaluation, and chatbot
  |
  +-- SQLite database (development default)
  +-- Celery worker -> Redis -> scrapers and matching tasks
```

### ⚙️ Backend modules

- `career_app/urls.py`: API routes and DRF router registration.
- `career_app/views.py`: API request handling and authentication boundaries.
- `career_app/models.py`: Profiles, academics, opportunities, matches, roles, courses, questions, and resume analyses.
- `career_app/serializers.py`: API response serializers.
- `career_app/ml_pipeline.py`: Gemini and resume-analysis orchestration.
- `career_app/local_nlp.py`: Offline resume, cover-letter, interview, and assistant fallbacks.
- `career_app/tasks.py`: Celery scraping, matching, and refresh tasks.
- `career_app/adapters/`: External opportunity source adapters.
- `career_app/management/commands/seed_db.py`: Seed roles and learning data.
- `core_project/settings.py`: Django, CORS, database, REST, Celery, media, and logging configuration.
- `core_project/celery.py`: Celery application and scheduled refresh configuration.

### 🖥️ Active frontend modules

- `templates/index.html`: Main application shell and UI views.
- `templates/static/js/app.js`: API calls, state, dashboard rendering, PDF preview, speech recognition, and interactions.
- `templates/static/css/style.css`: Shared frontend styles, scrollbar styling, animation classes, and Google Translate overrides.

## 🗃️ Data Model

- `StudentProfile`: authenticated or anonymous profile, target role, skills, gaps, projects, experience, improvements, questions, and readiness scores.
- `AcademicRecord`: degree, institution, graduation year, and CGPA linked to a student profile.
- `Opportunity`: normalized external or seeded opportunity with provider, type, mode, location, deadline, eligibility, and URL.
- `OpportunitySkill`: skills required by an opportunity.
- `ProfileMatch`: ranked relationship between a profile and an opportunity, including matching skills, reasoning, bookmark state, and cover letter.
- `CareerRole` and `RoleSkill`: seeded role taxonomy used by the local analysis path.
- `CourseRecommendation`: course suggestions associated with a skill.
- `InterviewQuestion`: seeded questions associated with a career role.
- `ResumeAnalysis`: historical analysis result and optional uploaded resume file for an authenticated user.

## 📂 Project Structure

```text
AI-Career_Portal/
├── career_app/
│   ├── adapters/
│   ├── management/commands/seed_db.py
│   ├── migrations/
│   ├── authentication.py
│   ├── local_nlp.py
│   ├── ml_pipeline.py
│   ├── models.py
│   ├── serializers.py
│   ├── tasks.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── core_project/
│   ├── asgi.py
│   ├── celery.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── templates/
│   ├── index.html
│   └── static/
│       ├── css/style.css
│       └── js/app.js
├── media/resumes/
├── db.sqlite3
├── manage.py
├── pyproject.toml
├── requirements.txt
├── uv.lock
├── .env.example
└── README.md
```

## 📋 Requirements

- Python 3.11 or newer.
- `uv` recommended, or Python `pip` with a virtual environment.
- Redis for Celery workers and asynchronous opportunity refreshes.
- Optional Gemini API key for cloud AI responses.
- Optional Adzuna and YouTube API credentials for those opportunity sources.
- Optional spaCy `en_core_web_sm` model for the local NLP path.

## 🛠️ Installation

```bash
git clone https://github.com/Harsh-GitHup/AI-Career_Portal.git
cd AI-Career_Portal
uv sync
```

With pip:

```bash
python -m venv .venv
.venv\\Scripts\\activate
python -m pip install -r requirements.txt
```

## 🔐 Configuration

Copy `.env.example` to `.env` and replace the placeholder values. Do not commit `.env` or expose its secrets.

```env
DJANGO_SECRET_KEY=replace-this-in-development
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

GOOGLE_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-3.8-flash

REDIS_URL=redis://127.0.0.1:6379/0
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0

ADZUNA_APP_ID=your-adzuna-app-id
ADZUNA_APP_KEY=your-adzuna-app-key
YOUTUBE_API_KEY=your-youtube-api-key
```

Configuration notes:

- `GOOGLE_API_KEY` is optional. Without it, resume analysis and supported assistant features use local fallbacks.
- `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` default to Redis on `127.0.0.1:6379/0`.
- SQLite is the default development database at `db.sqlite3`.
- CORS allows the local frontend at `http://localhost:3000` and `http://127.0.0.1:3000`.
- The project timezone is `Asia/Kolkata`.
- Set `DEBUG=False`, configure a real secret, restrict `ALLOWED_HOSTS`, and use HTTPS before production deployment.

## 🗄️ Database Initialization

```bash
uv run manage.py migrate
uv run manage.py seed_db
```

To seed from another compatible JSON file:

```bash
uv run manage.py seed_db --file path/to/core_career_data.json
```

The default seed file is `career-readiness-platform/Additional Scripts/core_career_data.json`. The archived directory is used as a data source by this command only; it is not the active frontend or backend.

## ▶️ Running Locally

### 🔌 Django API

```bash
uv run manage.py runserver
```

- API: `http://127.0.0.1:8000/api/`
- Admin: `http://127.0.0.1:8000/admin/`
- Development media: `http://127.0.0.1:8000/media/`

### 🌍 Static frontend

In a separate terminal:

```bash
uv run python -m http.server 3000 -d templates
```

Open `http://127.0.0.1:3000` in a browser. The frontend calls the API at `http://127.0.0.1:8000` and sends credentials for session authentication.

### ⚡ Celery worker

Start Redis first. On Windows, use the solo pool:

```bash
uv run celery -A core_project worker --loglevel=info -P solo
```

For scheduled refreshes, run Celery Beat separately:

```bash
uv run celery -A core_project beat --loglevel=info
```

The API can still serve synchronous requests when Redis is unavailable, but background scraping and matching will be skipped or retried.

## 🔗 API Reference

All routes are prefixed with `/api/`.

### 🔑 Authentication

| Method | Route                | Purpose                                            |
| ------ | -------------------- | -------------------------------------------------- |
| `POST` | `/api/register/`     | Create an account and initial student profile      |
| `POST` | `/api/login/`        | Start a session with username and password         |
| `POST` | `/api/logout/`       | End the current session                            |
| `POST` | `/api/social-login/` | Verify a Google OAuth ID token and start a session |

### 📑 Profile and resume

| Method                  | Route                  | Purpose                                                  |
| ----------------------- | ---------------------- | -------------------------------------------------------- |
| `GET/POST/PATCH/DELETE` | `/api/profiles/`       | Manage the authenticated user's profile                  |
| `GET/POST/PATCH/DELETE` | `/api/academics/`      | Manage academic records scoped to the authenticated user |
| `POST`                  | `/api/upload-resume/`  | Analyze a PDF and update profile data                    |
| `GET`                   | `/api/resume-history/` | List historical resume analyses                          |

### 🎯 Opportunities and recommendations

| Method | Route                                 | Purpose                                                 |
| ------ | ------------------------------------- | ------------------------------------------------------- |
| `GET`  | `/api/opportunities/`                 | List active opportunities                               |
| `GET`  | `/api/opportunities/types/`           | List distinct opportunity types                         |
| `GET`  | `/api/recommendations/`               | Get ranked matches grouped as opportunities and schemes |
| `POST` | `/api/bookmark/<match_id>/`           | Toggle a profile match bookmark                         |
| `POST` | `/api/cover-letter/<opportunity_id>/` | Generate or return a saved cover letter                 |
| `GET`  | `/api/cover-letter-history/`          | List saved cover letters for the authenticated user     |

Opportunity list query parameters include:

- `search`: search title, provider, description, and required skills.
- `type`: filter by opportunity type, case-insensitively.
- `is_free`: filter with `true` or `false`.
- `search` and DRF ordering parameters can be used with the configured list filters.

### 💬 Interview and assistant

| Method | Route                      | Purpose                                                         |
| ------ | -------------------------- | --------------------------------------------------------------- |
| `POST` | `/api/interview-evaluate/` | Evaluate a question and answer using Gemini or a local fallback |
| `POST` | `/api/chatbot/`            | Ask the authenticated contextual career assistant               |

Authenticated endpoints require the session created by login, registration, or social login. The frontend uses `credentials: 'include'` for cross-origin local development.

## 📤 Resume Upload Response

A successful resume upload returns the updated profile summary, including:

- `profile_id`
- `full_name`
- `target_role`
- `readiness_score`
- `extracted_skills`
- `skill_gaps`
- `recommended_courses`
- `resume_improvements`
- `interview_questions`
- `bio`
- `projects`
- `experience`
- `academic_records`

The upload flow also replaces the profile's current academic records, stores an authenticated history entry, and attempts to queue asynchronous scraping and matching.

## 🧪 Testing and Quality Checks

Run the Django configuration check:

```bash
uv run python manage.py check
```

Run the test suite:

```bash
uv run manage.py test
```

Run Python syntax validation:

```bash
uv run python -m compileall -q career_app core_project manage.py
```

Run formatting and lint checks:

```bash
uvx ruff format --check career_app core_project manage.py
uvx ruff check career_app core_project manage.py
```

Apply Ruff formatting only when intentionally updating formatting:

```bash
uvx ruff format career_app core_project manage.py
```

The existing tests cover authentication, opportunity listing and filters, recommendation grouping, profile authorization, bookmarks, history ownership, chatbot fallback behavior, cover-letter fallback behavior, interview evaluation fallback behavior, social-login errors, and mocked resume uploads.

## 🛡️ Security and Operational Notes

- Never commit `.env`, API keys, uploaded resumes, local databases, or generated caches.
- Keep authenticated querysets scoped to the current user.
- Use HTTPS and secure cookies in production.
- Replace the development `SECRET_KEY` and wildcard hosts before deployment.
- Configure a real database and persistent media storage for production.
- Redis is required for reliable background scraping and scheduled refreshes.
- External provider calls should be treated as optional because quota, network, and provider model availability can change.
- Uploaded documents should be valid, readable PDFs and should be validated before production use at the deployment boundary.

## 📦 Archived Material

The `career-readiness-platform/` directory contains a separate Vite prototype, archived backend copies, scripts, documentation, and seed data. It is retained for reference and is outside the active root application unless a task explicitly names it.

## 🤝 Contributing

1. Make a focused change in the active root application.
2. Preserve unrelated worktree changes and archived material.
3. Run the narrowest relevant test first.
4. Run Django checks and formatting/lint checks before opening a pull request.
5. Document API, model, configuration, or setup changes.

## 📜 License

See [LICENSE](LICENSE).
