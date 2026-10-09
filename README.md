# LinkPulse

A URL shortener with accounts and click analytics, built with Flask.

Create a short link (random or custom name), share it, and see how many people clicked,
per day and by source.

**Live demo:** _add your Render URL here after deploying_

## Features
- Sign up / log in (hashed passwords, session cookies)
- Short links with optional custom names
- Click tracking: time, referring site, browser
- Per-link stats page with a 14-day bar chart (pure SVG, no JS libraries)
- Delete links (and their click history)
- Security basics: CSRF tokens, safe-redirect check, URL validation (http/https only),
  security headers and a strict Content-Security-Policy
- 15 automated tests, run on every push with GitHub Actions

## Tech
Python 3.12, Flask, Flask-SQLAlchemy, Flask-Login, SQLite (local) / PostgreSQL (production),
Gunicorn, pytest.

## Run locally
```bash
git clone https://github.com/MahiSharma29/<REPO-NAME>.git
cd <REPO-NAME>/linkpulse
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
flask --app wsgi run --debug
```
Open http://127.0.0.1:5000

## Test
```bash
python -m pytest -q
```

## Configuration
| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Signs session cookies. Required in production. |
| `DATABASE_URL` | Optional. PostgreSQL URL. Defaults to local SQLite. |
| `FLASK_ENV` | Set to `production` to enforce a real secret key and secure cookies. |

## Project layout
```
app/
  __init__.py     app factory and config
  models.py       User, Link, Click
  auth.py         register / login / logout
  links.py        dashboard, redirect, stats, delete
  security.py     CSRF, security headers, safe redirect
  templates/ static/
tests/            pytest suite
wsgi.py           gunicorn entry point
```

## Ideas for next steps
Rate limiting, link expiry dates, QR codes, an API with tokens, Alembic migrations.
