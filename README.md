# LinkPulse 🔗⚡

A production-grade, lightweight URL shortening and click-tracking analytics platform built with Flask, SQLAlchemy, and PostgreSQL. LinkPulse delivers fast redirections, user authentication, and real-time click metrics via a clean, responsive web interface.

## 🌐 Live Deployment

* **Production URL:** <https://linkpulse-1-mmln.onrender.com/>

* **Health Check:** <https://linkpulse-1-mmln.onrender.com/health>

> *Note: Hosted on Render's free tier. If the instance has been idle, the initial request may take 30–50 seconds while the container spins up.*

## ✨ Key Features

* **Instant Link Shortening:** Generates collision-safe, randomized alphanumeric slugs for arbitrary target URLs.

* **Click Analytics & Auditing:** Automatically logs timestamps, IP address metadata, referrers, and user agents on every redirect.

* **User Authentication & Dashboard:** Session-based authentication powered by `Flask-Login` and `Werkzeug` secure password hashing.

* **CSRF Protection & Security Headers:** Built-in CSRF token protection on form submissions, strict cookie handling, and security middlewares.

* **Modular Application Architecture:** Clean separation using Flask application factories, blueprints (`auth`, `links`), and shared database models.

* **Automated CI/CD:** Continuous Integration pipeline via GitHub Actions validating 15 automated unit and integration tests on every commit.

## 🛠️ Architecture & Tech Stack

| Layer | Technologies | 
| ----- | ----- | 
| **Backend Framework** | Python 3.12+, Flask 3.1 | 
| **Database & ORM** | PostgreSQL (Render Managed), SQLite (Local Fallback), SQLAlchemy 2.0+ | 
| **WSGI Server** | Gunicorn 23.0 | 
| **Testing** | Pytest 8.3 (15 unit & integration suites) | 
| **Deployment Platform** | Render (Web Service + Managed PostgreSQL) | 
| **CI/CD** | GitHub Actions | 

## 📁 Repository Structure

```
LinkPulse/
├── app/
│   ├── __init__.py          # Flask application factory
│   ├── auth.py              # User authentication routes (register, login, logout)
│   ├── extensions.py        # SQLAlchemy & LoginManager instances
│   ├── links.py             # URL creation, redirection, and metric tracking
│   ├── models.py            # Relational database models (User, Link, ClickEvent)
│   ├── security.py          # CSRF protection and verification helpers
│   ├── static/              # Stylesheets and visual UI assets
│   └── templates/           # Jinja2 HTML layout and page templates
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Isolated test client and in-memory DB fixtures
│   └── test_app.py          # Pytest validation test suite
├── .github/
│   └── workflows/
│       └── linkpulse-ci.yml # Automated CI pipeline definition
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development and testing dependencies
├── wsgi.py                  # Production WSGI entry point
└── README.md                # Project documentation



```

## 🚀 Getting Started Locally

### Prerequisites

* Python 3.12+ installed

* Git installed

### 1. Clone the Repository

```
git clone https://github.com/MahiSharma29/LinkPulse.git
cd LinkPulse



```

### 2. Configure Virtual Environment

* **On Windows (Git Bash):**

  ```
  py -m venv .venv
  source .venv/Scripts/activate
  
  
  
  ```

* **On macOS / Linux:**

  ```
  python3 -m venv .venv
  source .venv/bin/activate
  
  
  
  ```

### 3. Install Dependencies

```
pip install -r requirements-dev.txt



```

### 4. Run Automated Tests

Execute the automated suite to verify route and database integrity:

```
python -m pytest -q
# Output expectation: 15 passed in ~5s



```

### 5. Start the Development Server

```
flask --app wsgi run --debug



```

Open <http://127.0.0.1:5000> in your browser.

## ⚙️ Environment Variables

LinkPulse defaults to a local SQLite database (`instance/linkpulse.sqlite`) in development. For production deployments, configure:

| Variable | Description | Example / Default | 
| ----- | ----- | ----- | 
| `SECRET_KEY` | Cryptographic key for session signing | `python -c "import secrets; print(secrets.token_hex(32))"` | 
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/dbname` | 
| `FLASK_ENV` | Application environment state | `production` | 
| `PYTHON_VERSION` | Runtime engine version | `3.12.3` | 

## 🚢 Render Deployment Summary

1. **Database:** Provision a Render PostgreSQL database (`linkpulse-db`) and retrieve the **Internal Database URL**.

2. **Web Service Configuration:**

   * **Runtime:** Python 3

   * **Build Command:** `pip install -r requirements.txt`

   * **Start Command:** `gunicorn wsgi:app`

3. **Environment Setup:** Inject `SECRET_KEY`, `DATABASE_URL`, and `FLASK_ENV=production`.

4. **Validation:** Query `/health` on the deployed domain to confirm operational readiness.

## 📄 License

This repository is licensed under the [MIT License](LICENSE).