# CareerAI - AI Career Portal

An advanced, AI-powered full-stack career platform designed to help students and professionals discover career opportunities, analyze their resumes, identify skill gaps, and prepare for interviews using state-of-the-art NLP models.

## 🚀 Exhaustive Feature List

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

- **Backend Engine:** Python, Django 5.x, Django REST Framework
- **Frontend UI:** Vanilla HTML/CSS/JS, Custom Tailwind-inspired CSS tokens, CSS Grid/Flexbox, Glassmorphism UI elements
- **Database Layer:** SQLite (default for development), ORM easily migratable to MySQL/PostgreSQL
- **Task Queue & Caching:** Celery 5.4 + Redis (For non-blocking AI inference and web scraping)
- **AI/ML Tooling:** LangChain, Google GenAI SDK, PyTorch, Transformers, spaCy, Scikit-learn
- **Package Management:** `uv` (Lightning-fast Python dependency resolving and syncing)

## 📂 Project Structure

```text
AI-Career_Portal/
│
├── career_app/                 # Main Django Application directory
│   ├── adapters/               # Contains universal_scraper.py for web scraping
│   ├── management/commands/    # Contains seed_db.py for dynamic ML fallback population
│   ├── authentication.py       # Custom CSRF-exempt session authentication logic
│   ├── local_nlp.py            # The offline Deep Learning HuggingFace/spaCy fallback engine
│   ├── ml_pipeline.py          # The primary LangChain/Gemini 3.8 Flash parsing pipeline
│   ├── models.py               # Database schemas (StudentProfile, Opportunity, CareerRole, etc.)
│   ├── serializers.py          # DRF serializers for API serialization
│   ├── tasks.py                # Celery background tasks (calculate_matches, run_scraper)
│   └── views.py                # REST API Views (Resume Upload, Chatbot, Opportunity Listing)
│
├── core_project/               # Django Settings & Core Configuration
│   ├── settings.py             # Configured for CORS, Logging, and Celery integration
│   └── urls.py                 # Core routing definitions
│
├── templates/                  # Frontend SPA UI
│   ├── index.html              # Single Page Application entry point (Glassmorphism layout)
│   └── static/                 # Frontend assets
│       ├── css/style.css       # Custom UI styling (Scrollbars, Translations)
│       └── js/                 # Application logic & DOM manipulation scripts
│
├── career-readiness-platform/  # Archival/Reference directory
│   └── (Contains original hackathon requirements (PDFs), old backend scripts, and screenshots)
│
├── manage.py                   # Django execution binary
├── pyproject.toml              # UV Project dependency and configuration definitions
├── uv.lock                     # UV highly-reproducible dependency locking
└── README.md                   # This file
```

## ⚙️ Getting Started & Setup

### 1. Clone & Install Dependencies

This project uses `uv` for lightning-fast package management instead of standard `pip`.

```bash
git clone https://github.com/Harsh-GitHup/AI-Career_Portal.git
cd AI-Career_Portal
uv sync
```

### 2. Environment Configuration

Create a `.env` file in the root directory and add the following keys. Ensure you have a running Redis instance on your local machine.

```env
DJANGO_SECRET_KEY=your_secret_key_here
DEBUG=True
ALLOWED_HOSTS=*
GOOGLE_API_KEY=your_gemini_api_key
REDIS_URL=redis://127.0.0.1:6379/0
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_APP_KEY=your_adzuna_app_key
YOUTUBE_API_KEY=your_youtube_api_key
```

### 3. Database Setup & Fallback Seeding

Apply database migrations. Then, run the custom seeder to populate the offline NLP fallback engine with standard foundational roles, skills, courses, and interview questions.

```bash
uv run manage.py migrate
uv run manage.py seed_db
```

### 4. Running the Application (Local Development)

The architecture is decoupled. You will need to spin up **three** separate terminal windows to run the Backend, Background Worker, and Frontend respectively.

#### Terminal 1: Django Backend API

```bash
uv run manage.py runserver
```

#### Terminal 2: Celery Worker (Task Queue)

Runs heavy asynchronous web scrapers and match engines in the background to prevent UI blocking.
_Note: `-P solo` is strictly required for Windows compatibility._

```bash
uv run celery -A core_project worker --loglevel=info -P solo
```

#### Terminal 3: Frontend Web Server

Serves the HTML templates to `http://localhost:3000`. The frontend will perform CORS requests to the Django backend.

```bash
uv run py -m http.server 3000 -d templates
```

## 🤝 Contributing

1. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Make focused changes and test locally.
3. Open a pull request with a clear description of the modifications.

## 📜 License

[LICENSE](LICENSE)
