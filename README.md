# CareerAI - AI Career Portal

CareerAI is a Django and Django REST Framework application that helps students and professionals analyze resumes, identify skill gaps, find career opportunities, and prepare for interviews.

> The active application uses a static HTML/CSS/JavaScript interface in `templates/` and a Python API in `career_app/`.
> `career-readiness-platform/` is archived/reference material and is not the frontend launched by the root Django project.

## 🚀 Features

- **Hybrid AI Resume Parsing Pipeline:**
  - **Primary Inference:** Gemini 3.8 Flash LLM for zero-shot resume analysis, structured data extraction (skills, matching roles, missing technical gaps, dynamic interview questions, and 3 actionable resume improvement tips).
  - **Robust Offline Fallback:** If the external API quota is exceeded or unavailable, the system automatically falls back to a locally processed ML pipeline. It uses HuggingFace `transformers` (`distilbert-base-uncased-mnli`) for zero-shot role classification, `spaCy` (`en_core_web_sm`) for Named Entity Recognition and syntactic noun chunking (skill extraction), and `sentence-transformers`.
- **Universal Opportunity Hub & Scraper:**
  - Asynchronous background scrapers utilizing `BeautifulSoup4`, `httpx`, and Google Dorks to bypass bot-blockers.
  - Aggregates Live Jobs (LinkedIn, Naukri, Adzuna API), Internships (Internshala, AICTE), Government Schemes (MMSKY), and Free Video Courses (NPTEL, YouTube Data API v3).
  - Implements smart deduplication using SHA-256 URL hashing.
- **Smart Interview Simulator & Audio Integration:**
  - Automatically analyzes resumes to dynamically generate 5 targeted technical and behavioral interview questions tailored precisely to the user's skillset and desired role.
  - Includes an Audio Interview Simulator powered directly by frontend `webkitSpeechRecognition` APIs for mock interviews.
- **Personalized Chatbot Assistant:**
  - Context-aware CareerAI assistant initialized with the user's career profile (target roles, existing skills) to provide hyper-specific, contextual career guidance instead of generic answers.
- **Document Viewer (PDF.js):**
  - Fully integrated `PDF.js` canvas renderer with customized dark-mode scrollbars (glassmorphism UI) for seamless resume previewing, replacing standard browser `iframe` rendering constraints.
- **Automated Cover Letter Generation:**
  - Leverages AI to draft professional, role-specific cover letters by cross-referencing the candidate's extracted profile with the scraped Opportunity descriptions.
- **Multilingual Support (Hindi Translation):**
  - Includes integrated Google Translate functionality (via custom `skiptranslate` CSS overrides) to seamlessly toggle the entire application interface and AI insights between English and Hindi, ensuring accessibility for a broader demographic.
- **Authentication Security:**
  - Secure, decoupled CSRF-exempt authentication bridging the gap between the static HTML frontend and the Django REST API backend, complete with Google OAuth support (`SocialLoginAPIView`).

## 🏗️ Architecture & Technology Stack

- **Backend Engine:** Python 3.11+, Django 5.x, Django REST Framework
- **Frontend UI:** Vanilla HTML/CSS/JS, Custom Tailwind-inspired CSS tokens, CSS Grid/Flexbox, Glassmorphism UI elements, Font Awesome, and PDF.js
- **Database Layer:** SQLite (default for development), ORM easily migratable to MySQL/PostgreSQL
- **Task Queue & Caching:** Celery 5.4 + Redis (For non-blocking AI inference and web scraping)
- **Web scraping:** Adzuna, YouTube Data API v3, LinkedIn, and Instaloader
- **AI/ML Tooling:** LangChain, Google GenAI SDK, Google Gemini, Pydantic, PyPDF, PyTorch, Transformers, spaCy, Scikit-learn
- **Package Management:** `uv` (Lightning-fast Python dependency resolving and syncing)

## 📂 Project Structure

```text
AI-Career_Portal/
├── career_app/
│   ├── adapters/               # Opportunity and web-scraping adapters
│   ├── management/commands/    # Database seeding command
│   ├── migrations/             # Django database migrations
│   ├── authentication.py       # CSRF-exempt session authentication
│   ├── local_nlp.py            # Offline resume parsing fallback
│   ├── ml_pipeline.py          # Gemini and resume-analysis orchestration
│   ├── models.py               # Profiles, opportunities, matches, and analyses
│   ├── serializers.py          # REST API serializers
│   ├── tasks.py                # Celery scraping, matching, and refresh tasks
│   ├── tests.py                # Django API tests
│   ├── urls.py                 # `/api/` routes
│   └── views.py                # REST API views
├── core_project/
│   ├── settings.py             # Django, CORS, database, Celery, and logging settings
│   ├── urls.py                 # `/admin/`, `/api/`, and development media routes
│   └── celery.py               # Celery application and nightly schedule
├── templates/
│   ├── index.html              # Active frontend application
│   └── static/                 # Frontend CSS and JavaScript
├── media/resumes/              # Uploaded resume files
├── manage.py
├── pyproject.toml              # Project metadata and dependencies
├── requirements.txt            # pip-compatible dependency list
├── .gitignore                  # Git ignore file
├── .env                        # Environment variables
├── README.md                   # Readme file
└── uv.lock                     # Locked uv dependency resolution
```

The nested `career-readiness-platform/` directory contains archived/reference material and a separate Vite prototype. It is not the frontend launched by the root Django project.

## ⚙️ Setup

### Requirements

- Python 3.11 or newer
- `uv` recommended, or `pip`
- Redis required for Celery workers and asynchronous tasks
- Optional: spaCy's `en_core_web_sm` model for the local NLP fallback

### Install

```bash
git clone https://github.com/Harsh-GitHup/AI-Career_Portal.git
cd AI-Career_Portal
uv sync
```

With pip, create and activate a virtual environment, then run:

```bash
python -m pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the repository root. `GOOGLE_API_KEY` is optional; without it, resume analysis uses the local fallback.

```env
DJANGO_SECRET_KEY=replace-this-in-development
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

GOOGLE_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-3.8-flash
ADZUNA_APP_ID=your-adzuna-app-id
ADZUNA_APP_KEY=your-adzuna-app-key
YOUTUBE_API_KEY=your-youtube-api-key

CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0
```

The Adzuna and YouTube variables enable their respective live sources. The default database is `db.sqlite3`; no separate database service is needed for local development.

### Initialize the Database

```bash
uv run manage.py migrate
uv run manage.py seed_db
```

The seed command creates baseline career roles, skills, course recommendations, and interview questions used by the local parser and recommendation features.

## Run Locally

Start Redis first, then use separate terminals for the Django server, Celery worker, and frontend server.

### Django API and static media

```bash
uv run manage.py runserver
```

The API is available at `http://127.0.0.1:8000/api/`. The Django admin is at `http://127.0.0.1:8000/admin/`.

### Celery worker

On Windows, use the solo pool:

```bash
uv run celery -A core_project worker --loglevel=info -P solo
```

Celery Beat schedules `nightly_refresh_all_profiles` for 02:00 Asia/Kolkata time. Run Beat separately when the scheduled refresh is required:

```bash
uv run celery -A core_project beat --loglevel=info
```

If Redis is unavailable, the API can still serve synchronous requests, but background scraping and matching will be skipped or retried.

### Static frontend

From the repository root:

```bash
uv run python -m http.server 3000 -d templates
```

Open `http://127.0.0.1:3000`. The frontend is configured for the API at `http://127.0.0.1:8000` and the Django settings allow CORS from ports 3000 on localhost and 127.0.0.1.

## API Overview

All API routes are prefixed with `/api/`.

- `POST /api/register/`, `POST /api/login/`, `POST /api/logout/`, `POST /api/social-login/`
- `GET|POST|PATCH|DELETE /api/profiles/`
- `GET|POST|PATCH|DELETE /api/academics/`
- `POST /api/upload-resume/`
- `GET /api/resume-history/`
- `GET /api/opportunities/` and `GET /api/opportunities/types/`
- `GET /api/recommendations/` and `POST /api/bookmark/<opportunity-match-id>/`
- `POST /api/cover-letter/<opportunity-id>/`
- `POST /api/interview-evaluate/`
- `POST /api/chatbot/`

The profile and academic endpoints, resume history, recommendations, cover letters, interview evaluation, and chatbot require authentication unless the view explicitly permits anonymous access.

## Verification and Formatting

Run the Django test suite:

```bash
uv run manage.py test
```

Run Python syntax, formatting, and lint checks:

```bash
uv run python -m compileall -q career_app core_project manage.py
uvx ruff format --check career_app core_project manage.py
uvx ruff check career_app core_project manage.py
```

Apply Ruff formatting with:

```bash
uvx ruff format career_app core_project manage.py
```

## AI Skill

> Read AGENTS.md and .claude/skills/source-audit/SKILL.md.
Then audit the active project according to those instructions.
Do not modify archived code.

These are example commands for invoking the custom dependency security skill:

- `/dependency-cve-audit audit all active dependencies`
  Scans project dependencies for CVEs, outdated packages, conflicts, and lockfile drift.

- `/dependency-cve-audit check CVE-XXXX-YYYY`
  Investigates a specific CVE and checks whether your project is affected.

- `/dependency-cve-audit upgrade the vulnerable package safely`
  Finds a compatible fixed version, updates the manifest/lockfile, then runs validation and rescans.

## 🤝 Contributing

1. Create a focused feature branch.
2. Run the relevant tests and formatting checks.
3. Open a pull request with a clear description of the change.

## 📜 License

[LICENSE](LICENSE)
