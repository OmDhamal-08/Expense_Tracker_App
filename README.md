# 🧾 Expense Tracker

A full-featured **personal finance management web application** built with Django. Track expenses and income, set budgets, monitor financial goals, and get automated alerts — all from a clean, responsive dashboard.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Django](https://img.shields.io/badge/Django-6.x-green?logo=django)
![DRF](https://img.shields.io/badge/DRF-REST%20API-red)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## ✨ Features

- 📊 **Dashboard** — Real-time snapshot of income, expenses, savings rate & budget status
- 💸 **Expense & Income Tracking** — With categories, tags, payment methods, receipts & location
- 📅 **Recurring Transactions** — Auto-generate daily / weekly / monthly / yearly entries
- 🎯 **Financial Goals** — Track savings, debt repayment & investments with progress bars
- 📈 **Reports & Analytics** — 12-month charts, category breakdowns, savings rate, CSV/PDF/JSON export
- 🔔 **Smart Notifications** — Budget warnings, goal milestones, weekly email summaries
- ⚡ **AJAX Quick-Add** — Add expenses instantly from any page without navigation
- ⌨️ **Keyboard Shortcuts** — `n` = new expense, `/` = search, `d` = dashboard
- 🌙 **Dark Mode** — Server-persisted theme preference across all devices
- 🔐 **Security** — 2FA (TOTP / Google Authenticator), rate limiting, JWT API auth
- 🌐 **Full REST API** — All features accessible via JSON API with Swagger docs

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Django 6, Python 3.12 |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **Auth** | django-allauth, django-otp (2FA), JWT (SimpleJWT) |
| **API** | Django REST Framework, drf-spectacular (OpenAPI/Swagger) |
| **Frontend** | Bootstrap 5, Chart.js, Font Awesome |
| **Deployment** | Gunicorn, WhiteNoise, Render |

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.12+
- Git

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/your-username/expense-tracker.git
cd expense-tracker

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
# Create expense_tracker/.env with the following:
```

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

```bash
# 5. Apply migrations
python manage.py migrate

# 6. Seed default categories & payment methods
python manage.py seed_defaults

# 7. Create an admin account
python manage.py createsuperuser

# 8. Run the server
python manage.py runserver
```

Visit **http://127.0.0.1:8000** 🎉

---

## 📁 Project Structure

```
expense-tracker/
├── accounts/          # Authentication, user profiles, 2FA
├── core/              # Expenses, income, budgets, goals, reports
│   └── management/commands/   # process_recurring, send_summary_email, seed_defaults
├── api/               # REST API (DRF) — serializers, views, routes
├── expense_tracker/   # Project settings, URLs, .env
├── templates/         # HTML templates (Django template engine)
├── static/            # CSS, JavaScript
├── requirements.txt
├── Procfile           # Gunicorn entry point (for Render/Heroku)
└── docker-compose.yml # Local PostgreSQL + pgAdmin
```

---

## 🌐 REST API

The full REST API is documented at **`/api/schema/swagger-ui/`** when the app is running.

### Authentication

```bash
# Register
POST /api/auth/register/   { email, password, password2 }

# Login → get JWT tokens
POST /api/auth/login/      { email, password }

# Use token in all requests
Authorization: Bearer <access_token>
```

### Key Endpoints

| Endpoint | Description |
|---|---|
| `GET/POST /api/expenses/` | List / create expenses |
| `GET/POST /api/income/` | List / create income |
| `GET/POST /api/budgets/` | List / create budgets |
| `GET/POST /api/goals/` | List / create goals |
| `GET /api/dashboard/` | Dashboard summary |
| `GET /api/stats/monthly/` | Monthly chart data |
| `GET /api/export/csv/` | Export CSV |
| `GET /api/export/pdf/` | Export PDF |

---

## 🏗️ Management Commands

```bash
# Auto-generate recurring transactions (run daily via cron)
python manage.py process_recurring

# Send weekly summary emails to all users
python manage.py send_summary_email

# Seed default categories and payment methods (run once on setup)
python manage.py seed_defaults
```

---

## ☁️ Deployment (Render)

This project is pre-configured for [Render](https://render.com).

1. Push your code to GitHub
2. Create a **Web Service** on Render → connect your repo
3. Set **Root Directory** to `expense-tracker`
4. Set **Build Command:**
   ```
   pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --no-input
   ```
5. Set **Start Command:** `gunicorn expense_tracker.wsgi:application`
6. Add a **PostgreSQL database** from Render dashboard
7. Add these **Environment Variables:**

| Variable | Value |
|---|---|
| `SECRET_KEY` | A long random string |
| `DEBUG` | `False` |
| `DATABASE_URL` | Render PostgreSQL URL |
| `ALLOWED_HOSTS` | `yourapp.onrender.com` |

> 📖 See [`PROJECT_DOCUMENTATION.md`](./PROJECT_DOCUMENTATION.md) for a complete guide to every feature, design decision, and technical detail.

---

## 🧪 Running Tests

```bash
python manage.py test
# Expected: Ran 9 tests in ~15s — OK
```

---

## 📄 License

This project is licensed under the MIT License.

---

## 👤 Author

Built by **Om Dhamal**  
GitHub: [@OmDhamal-08](https://github.com/OmDhamal-08)  
Repo: [Expense_Tracker_App](https://github.com/OmDhamal-08/Expense_Tracker_App)
