# AI-Powered Career Readiness & Employability Platform

**Team Name:** Tech Geeks 07
**Event:** MPOnline Idea & Innovation Hackathon 2026 (Technical Track)
**Challenge:** AI-Powered Career Readiness & Employability Platform

## 📌 Project Overview

The transition from "Campus to Corporate" is a critical hurdle for millions of graduates. This platform is a dynamic, AI-driven digital ecosystem that evaluates a student’s academic records and current technical competencies against real-time industry demands.

Unlike traditional static career portals, our AI engine utilizes concurrent processing to fetch live data from job boards, e-learning platforms, and government initiatives—specifically mapping local opportunities like the **MP Mukhyamantri Seekho Kamao Yojana** to a student's precise skill gaps.

## 🏗️ Technical Architecture

This project utilizes a highly decoupled, modern full-stack architecture designed for security, speed, and scalability.

* **Frontend (Angular):** Component-based architecture for a responsive, modular UI. Uses Angular Services and RxJS for robust state management.
* **Backend (Python / Django REST Framework):** Handles JWT authentication, custom ViewSets, and API routing.
* **Database (MySQL):** Relational data management mapping core user authentication to nested academic histories and unstructured JSON skill arrays.

## 🚀 Core Innovations

* **Dynamic Employability Score:** An algorithmic evaluation matching user JSON-mapped skills against industry baseline requirements.
* **Aggregator Architecture:** Utilizes Python's `ThreadPoolExecutor` to execute parallel HTTP requests to external APIs (job boards, YouTube Data API, government portals) to generate personalized roadmaps with zero UI blocking.
* **Hyper-Local Impact:** Algorithmically prioritizes Madhya Pradesh state empowerment initiatives to directly align with regional economic goals.

## ⚙️ Local Setup Instructions

### Backend (Django)

\`\`\`bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
\`\`\`

### Frontend (Angular)

*Access the application at `http://localhost:3000`*

## 📜 License

see [LICENSE](LICENSE)
