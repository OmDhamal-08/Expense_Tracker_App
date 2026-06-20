# Expense Tracker App

A full-stack Django personal finance application for tracking income, expenses, budgets, goals, reports, and AI-powered financial insights.

The app includes a server-rendered dashboard, secure authentication, REST APIs, export tools, multi-language support, and deployment-ready configuration for Render.

## Features

- Dashboard with monthly income, expenses, balance, recent transactions, and charts
- Expense and income tracking with categories, payment methods, tags, receipts, and recurring entries
- Budget management with progress tracking and alert thresholds
- Financial goals with progress calculation and milestone notifications
- Reports with category breakdowns, budget comparisons, and export options
- AI insights powered by Google Gemini
- Authentication with email login, Google OAuth, password reset, and TOTP-based 2FA
- REST API with JWT authentication and Swagger/OpenAPI documentation
- Data export as CSV, JSON, and PDF
- Dark mode, keyboard shortcuts, onboarding, and multi-language UI support

## Tech Stack

| Area | Technology |
| --- | --- |
| Backend | Python 3.12, Django 6 |
| API | Django REST Framework, SimpleJWT, drf-spectacular |
| Database | SQLite for development, PostgreSQL for production |
| Authentication | django-allauth, django-otp, django-ratelimit |
| Frontend | Django templates, CSS, Chart.js, Font Awesome |
| AI | Google Gemini API |
| Background jobs | django-apscheduler |
| Deployment | Gunicorn, WhiteNoise, Render |

## Project Structure

```text
Expense_Tracker_App/
|-- accounts/           # Authentication, profile, sessions, 2FA, exports
|-- api/                # REST API serializers, routes, and views
|-- core/               # Expenses, income, budgets, goals, reports, notifications
|-- expense_tracker/    # Django settings, root URLs, ASGI/WSGI
|-- static/             # Static assets
|-- templates/          # Django templates
|-- manage.py
|-- requirements.txt
|-- docker-compose.yml
|-- Procfile
`-- build.sh
```

## Getting Started

### Prerequisites

- Python 3.12+
- Git
- PostgreSQL optional for production-like local setup

### Installation

```bash
git clone https://github.com/OmDhamal-08/Expense_Tracker_App.git
cd Expense_Tracker_App

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
copy .env.example .env

python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

For macOS/Linux, activate the environment with:

```bash
source .venv/bin/activate
```

Open the app at:

```text
http://127.0.0.1:8000/
```

## Demo Account

After running `python manage.py seed_demo`, use:

```text
Email: demo@expensetracker.com
Password: Demo@1234
```

You can also use the demo login route:

```text
/accounts/demo-login/
```

## Environment Variables

Create a `.env` file from `.env.example` and update the values for your environment.

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
GEMINI_API_KEY=your-gemini-api-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

## Useful Commands

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py seed_demo --reset
python manage.py process_recurring
python manage.py send_summary_email
python manage.py test
```

## REST API

Swagger documentation is available at:

```text
/api/schema/swagger-ui/
```

Main API routes include:

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/api/auth/register/` | Register a user |
| POST | `/api/auth/login/` | Log in and receive JWT tokens |
| POST | `/api/auth/refresh/` | Refresh JWT access token |
| GET/POST | `/api/expenses/` | List or create expenses |
| GET/POST | `/api/income/` | List or create income |
| GET/POST | `/api/categories/` | List or create categories |
| GET/POST | `/api/payment-methods/` | List or create payment methods |
| GET/POST | `/api/budgets/` | List or create budgets |
| GET/POST | `/api/goals/` | List or create financial goals |
| GET | `/api/dashboard/` | Dashboard summary |
| GET | `/api/stats/monthly/` | Monthly analytics |
| GET | `/api/export/csv/` | Export CSV |
| GET | `/api/export/json/` | Export JSON |
| GET | `/api/export/pdf/` | Export PDF |

Authenticated API requests should include:

```text
Authorization: Bearer <access_token>
```

## Testing

Run the full test suite:

```bash
python manage.py test
```

Run focused tests:

```bash
python manage.py test core.tests
python manage.py test accounts.tests
```

## Deployment

The project includes files commonly used for Render deployment:

- `build.sh`
- `Procfile`
- `requirements.txt`
- WhiteNoise static file configuration
- `DATABASE_URL` support through `dj-database-url`

Typical Render settings:

```text
Build Command:
pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --no-input

Start Command:
gunicorn expense_tracker.wsgi:application
```

Recommended production environment variables:

```env
SECRET_KEY=your-production-secret-key
DEBUG=False
DATABASE_URL=your-render-postgres-url
ALLOWED_HOSTS=your-app.onrender.com
GEMINI_API_KEY=your-gemini-api-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

## Repository Description

Django personal finance tracker with dashboards, budgeting, goals, REST APIs, exports, authentication, multi-language support, and AI-powered insights.

## Author

Om Dhamal

GitHub: https://github.com/OmDhamal-08
