# AI-Powered Career Readiness & Employability Platform

**Team Name:** Tech Geeks 07
**Event:** MPOnline Idea & Innovation Hackathon 2026 (Technical Track)
**Challenge:** AI-Powered Career Readiness & Employability Platform

## 📌 Project Overview

The transition from "Campus to Corporate" is a critical hurdle for millions of graduates. This platform is a dynamic, AI-driven digital ecosystem that evaluates a student’s academic records and current technical competencies against real-time industry demands.

Unlike traditional static career portals, our AI engine utilizes concurrent processing to fetch live data from job boards, e-learning platforms, and government initiatives—specifically mapping local opportunities like the **MP Mukhyamantri Seekho Kamao Yojana** to a student's precise skill gaps.

## 🏗️ Technical Architecture

This project is implemented as a Django-based career intelligence platform with a modular service-oriented backend and a single-page dashboard served from the Django app itself.

* **Presentation Layer:** A server-rendered Tailwind-based dashboard in `templates/index.html` enables the student experience, including resume upload, skill gap visualization, mock interview content, and government opportunity listings.
* **API Layer:** Django REST Framework exposes endpoints such as resume ingestion, opportunity catalog search, and recommendation generation in `career_app/views.py` and `career_app/urls.py`.
* **AI Resume Parsing Engine:** `career_app/ml_pipeline.py` reads uploaded PDF resumes using `PyPDFLoader`, extracts text, and calls Google Gemini through LangChain to generate structured outputs for:
  * detected candidate name
  * target job roles
  * extracted skills
  * missing skill gaps
  * recommended learning paths
  * resume improvement suggestions
  * mock interview questions
* **Data Layer:** MySQL-compatible Django ORM models in `career_app/models.py` manage student profiles, opportunities, opportunity skill metadata, and profile-to-opportunity match scores.
* **Opportunity Aggregation & Matching:** `career_app/tasks.py` orchestrates background ingestion and match scoring using Celery workers. Skill and opportunity data is normalized through adapters in `career_app/adapters/`.
* **External Data Sources:**
  * government schemes and certified courses are seeded through `GovtSchemesAdapter` and `CoursePortalAdapter`
  * live commercial jobs can be pulled through `CommercialJobsAdapter` when `RAPIDAPI_KEY` is configured
  * Redis acts as the broker/result backend for Celery tasks
* **Background Processing:** Async scoring and scraper jobs allow the platform to analyze resumes and populate opportunities without blocking the main request flow.

## 🚀 Core Innovations

* **Dynamic Employability Score:** The system compares a candidate’s extracted skills against opportunity skill requirements and produces a readiness score and ranked recommendation list.
* **AI-Driven Resume Intelligence:** Gemini-powered parsing transforms raw PDF content into structured skill analysis and actionable career guidance.
* **Opportunity Aggregator Architecture:** Adapters normalize heterogeneous public and government data sources into a unified opportunity catalog with deduplication and relevance matching.
* **Hyper-Local Impact:** The platform prioritizes Madhya Pradesh programs and public initiatives such as the MP Mukhyamantri Seekho Kamao Yojana while also surfacing national courses and jobs.

## ⚙️ Local Setup Instructions

### 1) Prerequisites

Before running the project locally, install:

* Python 3.11+
* MySQL 8+
* Redis Server
* A Google AI API key for Gemini (`GOOGLE_API_KEY`)
* Optional: RapidAPI key for live job feeds (`RAPIDAPI_KEY`)

### 2) Clone and create a virtual environment

```bash
git clone <your-repository-url>
cd "AI Career Portal"
python -m venv .venv
```

Activate the environment:

```bash
# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3) Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4) Configure environment variables

Create a `.env` file in the project root with values similar to the following:

```env
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=career_portal_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306

GOOGLE_API_KEY=your_google_gemini_key
GEMINI_MODEL=gemini-3.8-flash

CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0

RAPIDAPI_KEY=your_optional_rapidapi_key
```

### 5) Create the MySQL database

```sql
CREATE DATABASE career_portal_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Then run database migrations:

```bash
python manage.py migrate
```

### 6) Start Redis and Celery workers

Start Redis:

```bash
redis-server
```

In a separate terminal:

```bash
celery -A core_project worker -l info
```

Optional scheduler for recurring ingestion jobs:

```bash
celery -A core_project beat -l info
```

### 7) Run the Django app

```bash
python manage.py runserver 0.0.0.0:8000
```

Open the application at:

* Dashboard: `http://localhost:8000/`
* Admin: `http://localhost:8000/admin/`
* API base: `http://localhost:8000/api/`

### 8) Typical flow

1. Upload a PDF resume from the dashboard.
2. The AI pipeline analyzes the resume and saves the extracted profile.
3. Matching opportunities are generated asynchronously through Celery.
4. The dashboard displays readiness scores, skill gaps, resume recommendations, and recommended schemes/jobs.

## 📜 License

see [LICENSE](LICENSE)
