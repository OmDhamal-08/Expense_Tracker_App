# 💰 Expense Tracker — Full-Stack Django Finance App

A **production-grade personal finance management application** built with Django 6, featuring AI-powered insights, a full REST API, and a modern dashboard with real-time analytics.

[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://python.org)
[![Django 6](https://img.shields.io/badge/Django-6.x-092E20?logo=django&logoColor=white)](https://djangoproject.com)
[![DRF](https://img.shields.io/badge/REST_API-DRF-FF6F61?logo=django&logoColor=white)](https://django-rest-framework.org)
[![Gemini AI](https://img.shields.io/badge/AI-Gemini_2.0-4285F4?logo=google&logoColor=white)](https://ai.google.dev)
[![Tests](https://img.shields.io/badge/Tests-56_passing-2DC653?logo=pytest&logoColor=white)](#-testing)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🚀 Live Demo

> **Try instantly — no sign-up required!**
>
> Click **"Try Demo"** on the home page or visit `/accounts/demo-login/`
>
> Pre-filled with **6 months of realistic financial data** (194 expenses, 12 income records, 6 budgets, 3 goals).
>
> **Demo credentials:** `demo@expensetracker.com / Demo@1234`

---

## ✨ Key Features

### Core Financial Management
| Feature | Description |
|---------|-------------|
| 📊 **Smart Dashboard** | Real-time income/expense/savings overview with 6-month trend charts |
| 💸 **Expense & Income Tracking** | Categories, tags, payment methods, receipt uploads, location |
| 📅 **Recurring Transactions** | Auto-generate daily/weekly/monthly/yearly entries |
| 🎯 **Financial Goals** | Track savings, debt repayment & investments with progress bars |
| 📈 **Reports & Analytics** | 12-month charts, category breakdowns, savings rate |

### AI & Intelligence
| Feature | Description |
|---------|-------------|
| 🤖 **AI Insights (Gemini)** | Personalized spending analysis, savings tips & risk alerts powered by Google Gemini AI |
| 🔔 **Smart Notifications** | Automatic budget warnings & goal milestone alerts |
| 📊 **Budget vs Actual** | Visual comparison of budgeted vs actual spending |

### Security & API
| Feature | Description |
|---------|-------------|
| 🔐 **2FA Authentication** | TOTP via Google Authenticator |
| 🌐 **Full REST API** | 20+ endpoints with JWT auth & Swagger docs |
| 🛡️ **Rate Limiting** | Brute-force protection on auth endpoints |
| 📤 **Data Export** | CSV, JSON & PDF export |

### UX Polish
| Feature | Description |
|---------|-------------|
| 🌙 **Dark Mode** | Server-persisted theme |
| ⌨️ **Keyboard Shortcuts** | `n` = new expense, `d` = dashboard, `/` = search |
| ⚡ **AJAX Quick-Add** | Add expenses without page navigation |
| 🌍 **Multi-language** | English, Hindi, Marathi |
| 🔑 **Google OAuth** | One-click social login |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 6, Python 3.12 |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **AI** | Google Gemini 2.0 Flash API |
| **Auth** | django-allauth, django-otp (2FA), JWT (SimpleJWT) |
| **API** | Django REST Framework, drf-spectacular (OpenAPI/Swagger) |
| **Frontend** | Bootstrap 5, Chart.js, Font Awesome, marked.js |
| **Deployment** | Gunicorn, WhiteNoise, Render |
| **DevOps** | Docker Compose, GitHub Actions |

---

## 📁 Project Structure

```
expense-tracker/
├── accounts/                  # Auth, profiles, 2FA, sessions, Google OAuth
├── core/                      # Expenses, income, budgets, goals, reports
│   ├── insights.py            # Gemini AI integration
│   ├── management/commands/
│   │   └── seed_demo.py       # Demo data seeder (194 expenses, 6 months)
│   └── tests/                 # 56 unit & integration tests
│       ├── test_models.py     # Model tests (Budget logic, Goal %, etc.)
│       └── test_views.py      # View tests (CRUD, auth, exports, etc.)
├── api/                       # REST API (DRF) — serializers, views, routes
│   └── views/                 # Modular API views (auth, transactions, etc.)
├── expense_tracker/           # Settings, root URLs
├── templates/                 # Django templates
├── static/                    # CSS, JS
├── requirements.txt
├── Procfile                   # Gunicorn (Render/Heroku)
└── docker-compose.yml         # Local PostgreSQL + pgAdmin
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Git

### Setup

```bash
# 1. Clone
git clone https://github.com/OmDhamal-08/Expense_Tracker_App.git
cd Expense_Tracker_App

# 2. Virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env         # Edit with your keys

# 5. Migrate & seed
python manage.py migrate
python manage.py seed_demo   # Creates demo user with 6 months of data

# 6. Run
python manage.py runserver
```

Visit **http://127.0.0.1:8000** and click **"Try Demo"** 🎉

### Environment Variables

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
GEMINI_API_KEY=your-gemini-api-key     # For AI Insights
GOOGLE_CLIENT_ID=                       # For Google OAuth
GOOGLE_CLIENT_SECRET=
```

---

## 🌐 REST API

Swagger UI: **`/api/schema/swagger-ui/`** (auto-generated from code)

### Authentication

```bash
# Register
POST /api/auth/register/    { email, password, password2 }

# Login → JWT tokens
POST /api/auth/login/       { email, password }

# All requests:
Authorization: Bearer <access_token>
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET/POST` | `/api/expenses/` | List / create expenses |
| `GET/PUT/DELETE` | `/api/expenses/<id>/` | Retrieve / update / delete |
| `GET/POST` | `/api/income/` | List / create income |
| `GET/POST` | `/api/budgets/` | List / create budgets |
| `GET/POST` | `/api/goals/` | List / create goals |
| `GET` | `/api/dashboard/` | Dashboard summary |
| `GET` | `/api/stats/monthly/` | Monthly chart data |
| `GET` | `/api/export/csv/` | Export as CSV |
| `GET` | `/api/export/pdf/` | Export as PDF |
| `GET` | `/api/export/json/` | Export as JSON |

---

## 🧪 Testing

```bash
python manage.py test core.tests --verbosity=2

# 56 tests covering:
# - 22 unit tests (models: Budget %, Goal progress, Category constraints)
# - 34 integration tests (views: CRUD, auth guards, exports, bulk ops)
```

**What's tested:**
- ✅ All model properties (spent_percentage, is_over_budget, progress_percentage)
- ✅ Auth guards (anonymous users redirected on all 7 protected routes)
- ✅ Full CRUD lifecycle (create → edit → delete) for expenses, income, budgets, goals
- ✅ Cross-user data isolation (user A can't edit user B's expenses)
- ✅ Bulk delete operations
- ✅ Search & filter functionality
- ✅ CSV/JSON export responses
- ✅ Notification read/clear workflows
- ✅ Goal completion triggers notification

---

## 🏗️ Management Commands

```bash
python manage.py seed_demo              # Seed demo user with sample data
python manage.py seed_demo --reset      # Wipe & re-seed demo data
python manage.py process_recurring      # Auto-generate recurring txns (cron)
python manage.py send_summary_email     # Weekly email summaries
```

---

## ☁️ Deployment (Render)

1. Push to GitHub
2. Create **Web Service** on Render → connect repo
3. **Build Command:**
   ```
   pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --no-input && python manage.py seed_demo
   ```
4. **Start Command:** `gunicorn expense_tracker.wsgi:application`
5. Add PostgreSQL database from Render dashboard
6. Set environment variables:

| Variable | Value |
|----------|-------|
| `SECRET_KEY` | Long random string |
| `DEBUG` | `False` |
| `DATABASE_URL` | Render PostgreSQL URL |
| `ALLOWED_HOSTS` | `yourapp.onrender.com` |
| `GEMINI_API_KEY` | Your Gemini API key |

---

## 📄 License

MIT License — see [LICENSE](LICENSE)

---

## 👤 Author

**Om Dhamal**

[![GitHub](https://img.shields.io/badge/GitHub-@OmDhamal--08-181717?logo=github)](https://github.com/OmDhamal-08)

📧 Contact via GitHub

---

> 📖 For deep technical details and interview prep, see [`INTERVIEW_PREPARATION.md`](./INTERVIEW_PREPARATION.md)
