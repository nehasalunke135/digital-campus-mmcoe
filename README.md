# Digital Campus — Unified Academic & Collegiate Ecosystem

An institutional, unified digital campus portal engineered for modern university and collegiate environments. The platform integrates academic services, interactive wayfinding, career discovery, and student community discussions into a single, cohesive web application.

---

## 1. Project Modules

1. **Digital Campus Dashboard (`/`)**
   - Central institutional gateway providing authentication, academic profile overview, verified student credentials, quick service links, and responsive navigation.

2. **Campus Navigator (`/navigator/`)**
   - Interactive, multi-floor wayfinding map with room search, building exploration, accessibility routes, and department-level spatial directory.

3. **InterX Career Hub (`/interx/`)**
   - Collegiate opportunity discovery engine for verified internships, research projects, technical hackathons, and direct applications.

4. **CollegeConnect (`/community/`)**
   - Peer collaboration feed featuring college club announcements, academic discussions, interactive comments, and student profiles.

---

## 2. Technology Stack

* **Backend Framework:** Django (v6.1.1)
* **API Engine:** Django REST Framework (DRF)
* **Authentication:** DRF TokenAuthentication & SessionAuthentication
* **Production Web Server:** Gunicorn & WhiteNoise
* **Database:** SQLite (default / demo) with PostgreSQL compatibility via `dj-database-url`
* **Frontend Modules:** HTML5, CSS3, JavaScript (ES6+), React 18, TypeScript, Tailwind CSS, TanStack Router
* **Runtime:** Python 3.13

---

## 3. Project Architecture & Structure

```
common interface/
├── backend/
│   ├── accounts/          # User models, role authorization, login/registration APIs
│   ├── comments/          # Discussion comments API
│   ├── interx/            # Internships and hackathons models & APIs
│   ├── mmcoe_portal/      # Django settings, WSGI, unified URL router
│   ├── posts/             # Community post feeds and profile extensions
│   ├── db.sqlite3         # SQLite database instance
│   ├── manage.py          # Django management script
│   └── requirements.txt   # Python dependency specifications
├── community/             # CollegeConnect production static bundle
├── interx/                # InterX Career Hub production static bundle
├── navigator/             # Campus Navigator production static bundle
├── media/                 # User-uploaded assets (avatars, attachments)
├── static/                # Institutional styling, images, and helper scripts
├── js/                    # Core API client and authentication managers
├── index.html             # Central Digital Campus entry portal
├── script.js              # Portal UI controller and responsive mobile drawer
├── style.css              # Adaptive institutional stylesheet
├── .gitignore             # Repository exclusion rules
└── README.md              # Project documentation
```

---

## 4. Main Application Routes

| Path | Purpose | Type |
| :--- | :--- | :--- |
| `/` | Central Portal: Sign In, Register & Academic Overview | Server-rendered Template |
| `/navigator/` | Interactive Campus Wayfinding Map & Floor Plans | Pre-built SPA Bundle |
| `/interx/` | Internships, Hackathons & Opportunity Hub | Pre-built SPA Bundle |
| `/community/` | Student Community, Discussions & Profiles | Pre-built SPA Bundle |
| `/api/auth/` | Central Authentication Endpoints (Login, Logout, Me) | REST API |
| `/api/interx/` | Internships & Hackathons Data Services | REST API |
| `/api/v1/posts/` | Collegiate Discussions & Feed Management | REST API |
| `/api/v1/comments/`| Discussion Comments & Threading | REST API |

---

## 5. Authentication Architecture

The application implements a **Unified Institutional Authentication** pattern:
* Credentials are authenticated centrally at `/api/auth/login/` via email address or Student ID.
* Upon successful validation, a persistent DRF authentication token (`TokenAuthentication`) is returned and stored securely in `localStorage` under the shared key `mmcoe_auth_token`.
* All sub-modules (`/navigator/`, `/interx/`, `/community/`) share this single authentication context, enabling single sign-on across the entire domain without multiple logins.
* Logout at `/api/auth/logout/` revokes the token and clears client state across all modules.

---

## 6. Local Setup Instructions

### Prerequisites
* Python 3.12 or 3.13 installed
* Git

### Step-by-Step Run Guide

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd "common interface"
   ```

2. **Create and activate a virtual environment (optional but recommended):**
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Run migrations (if applicable):**
   ```bash
   python backend/manage.py migrate
   ```

5. **Start the local development server:**
   ```bash
   python backend/manage.py runserver 127.0.0.1:8000
   ```

6. **Open in browser:**
   Navigate to `http://127.0.0.1:8000/`.

---

## 7. Demo Credentials (For Testing)

For evaluation and demonstration purposes, pre-configured accounts are available in the database:

* **Student Account:**
  * **Identifier:** `<registered-student-email>`
  * **Password:** `<student-password>`
* **Administrator Account:**
  * **Identifier:** `<registered-admin-email>`
  * **Password:** `<admin-password>`

*(Refer to internal deployment notes or administrator handoff documents for active evaluation credentials.)*

---

## 8. Deployment Notes (Render)

This project is architected for deployment as a **single Render Web Service**:

* **Environment:** Python 3 (`PYTHON_VERSION=3.13.2`)
* **Build Command:**
  ```bash
  pip install -r backend/requirements.txt && python backend/manage.py migrate
  ```
* **Start Command:**
  ```bash
  gunicorn --chdir backend mmcoe_portal.wsgi:application --bind 0.0.0.0:$PORT
  ```
* **Environment Variables:**
  * `PYTHON_VERSION`: `3.13.2`
  * `SECRET_KEY`: `<generate-random-secret-key>`
  * `DEBUG`: `False`
  * `ALLOWED_HOSTS`: `*` (or `.onrender.com`)
