# 🧾 Django Expense Tracker — Full Project Documentation

> **Purpose of this document:** This is the single source of truth for understanding everything about this project — what was built, why every decision was made, how each piece works, what alternatives were considered, and the full development workflow. Anyone reading this — whether a new developer, interviewer, or project evaluator — should come away with a complete understanding of the system.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Why We Built This / The Problem Being Solved](#2-why-we-built-this)
3. [Technology Stack — What We Used & Why](#3-technology-stack)
4. [Project Structure](#4-project-structure)
5. [Database Models — The Heart of the App](#5-database-models)
6. [Application Modules (Apps)](#6-application-modules)
7. [REST API Layer](#7-rest-api-layer)
8. [Security Features](#8-security-features)
9. [Advanced Features Explained](#9-advanced-features)
10. [Complete URL / Route Map](#10-url-map)
11. [Configuration & Environment Variables](#11-configuration)
12. [Development Workflow](#12-development-workflow)
13. [Management Commands (Automation)](#13-management-commands)
14. [Testing Strategy](#14-testing-strategy)
15. [Deployment](#15-deployment)
16. [Design Decisions — Why NOT Something Else](#16-design-decisions)
17. [Common Questions & Answers](#17-common-questions)

---

## 1. Project Overview

**Project Name:** Expense Tracker  
**Framework:** Django 6.x (Python)  
**Type:** Full-stack web application with a REST API layer  
**Database:** SQLite (development) / PostgreSQL (production)  
**Authentication:** Email-based login + Two-Factor Authentication (TOTP)

### What This App Does

The Expense Tracker is a **personal finance management web application** that allows users to:

- Track all **expenses and income** with rich metadata (category, payment method, location, tags, receipts)
- Set and monitor **budgets** per category with configurable alert thresholds
- Define and track **financial goals** (savings, debt repayment, investments, etc.)
- View detailed **reports and analytics** including charts, trends, and savings rates
- Automate **recurring transactions** (daily, weekly, monthly, yearly)
- Get **email notifications** for budget warnings and goal milestones
- Export data as **CSV, JSON, or PDF**
- Access all features through a **REST API** (useful for mobile apps or integrations)

---

## 2. Why We Built This

### The Problem

Most people have no real-time awareness of where their money goes. Spreadsheets are too manual. Banking apps show transactions but don't help with budgeting goals or forecasting. This project solves that by providing:

1. **A single dashboard** showing real-time financial snapshot
2. **Budget enforcement** with alerts before you overspend
3. **Goal tracking** so long-term savings targets stay visible
4. **Automation** so recurring bills/subscriptions don't have to be entered manually
5. **An API** so the data can be used by any frontend or mobile client

### Why Django (and not something else)?

- Django provides **batteries-included** features: ORM, admin panel, auth, sessions, forms — all ready to use without configuration
- Django's MTV (Model-Template-View) pattern is **well-understood** and very maintainable for data-heavy apps
- Django REST Framework (DRF) adds a world-class API layer on top with minimal code
- Django has **built-in security** against XSS, CSRF, SQL injection, clickjacking — crucial for a financial app
- Strong ecosystem: `django-allauth`, `django-otp`, `django-taggit`, `drf-spectacular` all have first-class Django support

---

## 3. Technology Stack

### Core Framework

| Package | Version | Why We Used It | Why NOT an Alternative |
|---|---|---|---|
| **Django** | 6.x | Full-stack Python web framework with ORM, templates, admin, auth | Flask would require manually adding every feature Django provides out of the box |
| **Python** | 3.12+ | Language of Django; large ecosystem, readable syntax | N/A — Django is Python-only |

### Database

| Package | Why Used | Why Not Alternative |
|---|---|---|
| **SQLite** (dev) | Zero-config file-based DB, perfect for development and testing | PostgreSQL requires a running server — overkill locally |
| **PostgreSQL** (prod) | Production-grade, reliable, handles concurrent users | MySQL is fine too, but PostgreSQL has better support in Django ecosystem |
| **`dj-database-url`** | Parses a single `DATABASE_URL` env var into Django's `DATABASES` dict | Makes switching from SQLite to Postgres trivially easy — just change one env variable |
| **`psycopg2-binary`** | PostgreSQL driver for Python | Required for Django to talk to PostgreSQL |

### Authentication

| Package | Why Used | Why Not Alternative |
|---|---|---|
| **`django-allauth`** | Handles email login, signup, password reset, email verification | Django's built-in auth uses usernames — we wanted email-only login; allauth supports this natively |
| **Custom `User` model** | `AbstractUser` extended to use `email` as `USERNAME_FIELD` | Django's default `User` uses `username`; changing later is very hard — so we customized it from the start |
| **`django-otp`** | TOTP-based Two-Factor Authentication (Google Authenticator compatible) | SMS 2FA requires paid providers; TOTP is free, offline-capable, and more secure |
| **`rest_framework_simplejwt`** | JWT tokens for API authentication | Session auth doesn't work well for REST APIs; JWT is stateless and standard |

### Forms & UI

| Package | Why Used |
|---|---|
| **`django-crispy-forms`** | Renders Django forms as Bootstrap 5 with one template tag — no manual HTML form coding |
| **`crispy-bootstrap5`** | The Bootstrap 5 template pack for crispy-forms |
| **Bootstrap 5** | Industry-standard responsive CSS framework — widely known, fast to build with |
| **Chart.js** | Lightweight JavaScript chart library — used for Income vs Expense bar charts in Reports |
| **Font Awesome** | Icon library used for category icons, UI buttons |

### API Layer

| Package | Why Used | Why Not Alternative |
|---|---|---|
| **Django REST Framework (DRF)** | The gold-standard for building REST APIs in Django | Flask-RESTful or FastAPI would mean rewriting the entire auth and model layer |
| **`drf-spectacular`** | Auto-generates OpenAPI 3.0 schema + Swagger UI from DRF views | `drf-yasg` is older and supports OpenAPI 2.0 only; `drf-spectacular` is actively maintained |
| **JWT (SimpleJWT)** | Stateless token auth for the API | API keys require custom management; OAuth2 is complex for a personal app |
| **`django-filter`** | Clean filterable querysets for list endpoints (filter by date, category, etc.) | Writing manual filter logic in views is error-prone and repetitive |

### Tagging

| Package | Why Used |
|---|---|
| **`django-taggit`** | Adds many-to-many tagging to any model with a single `TaggableManager()` field |

Why `django-taggit` and not storing tags as a `CharField`?  
→ `CharField` for tags means you can't filter by tag, relate tags across expenses, or query "all expenses tagged #vacation" without string parsing. `taggit` stores tags in a proper normalized table with full ORM query support.

### File Handling & Export

| Package | Why Used |
|---|---|
| **Pillow** | Image processing — used for profile pictures and receipt uploads |
| **`xhtml2pdf`** | Converts HTML templates to PDF for report exports |
| **Django's built-in CSV** | Python's `csv` module via Django's `HttpResponse` for CSV exports |

### Static Files & Deployment

| Package | Why Used | Why Not Alternative |
|---|---|---|
| **WhiteNoise** | Serves static files directly from Django in production without a CDN | No need for Nginx just for static files; WhiteNoise handles compression + caching headers |
| **Gunicorn** | Production WSGI server for Django | Django's built-in dev server is single-threaded and not suitable for production |
| **`python-decouple`** | Reads settings from `.env` files and environment variables | `os.environ.get()` works but `decouple` provides type casting, defaults, and `.env` file support cleanly |

---

## 4. Project Structure

```
expense-tracker/
│
├── expense_tracker/         # Django project settings package
│   ├── settings.py          # All app configuration
│   ├── urls.py              # Root URL dispatcher
│   ├── wsgi.py              # WSGI entry point (for Gunicorn / production)
│   ├── asgi.py              # ASGI entry point (for async support)
│   └── .env                 # Environment variables (SECRET_KEY, DB URL, etc.)
│
├── accounts/                # App: User authentication & profiles
│   ├── models.py            # Custom User model (email-based), UserSession model
│   ├── views.py             # Login, register, profile, password change views
│   ├── views_2fa.py         # Two-factor authentication views (setup, verify)
│   ├── views_extras.py      # Helper views (onboarding etc.)
│   ├── forms.py             # Login, register, profile update forms
│   ├── signals.py           # Post-save signals (e.g., auto-create profile)
│   └── urls.py              # Auth URL patterns (/login, /register, /profile)
│
├── core/                    # App: Core business logic (expenses, income, budgets)
│   ├── models.py            # Category, Expense, Income, Budget, FinancialGoal, Notification
│   ├── views.py             # All views for CRUD, dashboard, reports, analytics
│   ├── forms.py             # Expense, Income, Budget, Goal forms
│   ├── urls.py              # Core URL patterns (/expenses, /budgets, /reports...)
│   ├── admin.py             # Django admin customizations
│   ├── emails.py            # Email sending logic (budget warnings, summaries)
│   ├── context_processors.py # Injects global context (unread notifications count etc.)
│   ├── templatetags/        # Custom Django template tags/filters
│   └── management/
│       └── commands/
│           ├── process_recurring.py    # Auto-generates recurring transactions
│           ├── send_summary_email.py   # Sends weekly summary emails
│           └── seed_defaults.py        # Seeds default categories/payment methods
│
├── api/                     # App: REST API layer (DRF)
│   ├── serializers.py       # DRF serializers for all models
│   ├── urls.py              # API URL patterns (/api/expenses, /api/auth...)
│   └── views/
│       ├── auth.py          # Register, Login, Logout, Profile API views
│       ├── transactions.py  # Expense & Income CRUD API views
│       ├── categories.py    # Category & PaymentMethod API views
│       ├── planning.py      # Budget & Goal API views
│       ├── dashboard.py     # Dashboard summary API view
│       ├── exports.py       # CSV, PDF, JSON export API views
│       └── stats.py         # Monthly stats, Notifications API views
│
├── templates/               # All HTML templates
│   ├── base.html            # Base layout (navbar, dark mode, JS imports)
│   ├── home.html            # Landing/home page
│   ├── accounts/            # Auth templates (login.html, register.html...)
│   └── core/
│       ├── dashboard.html
│       ├── expenses/        # expense_list.html, expense_form.html...
│       ├── budgets/
│       ├── goals/
│       ├── reports/
│       └── partials/
│           └── quick_add_form.html  # AJAX partial form for quick expense entry
│
├── static/                  # CSS, JavaScript, images
├── media/                   # User uploaded files (receipts, profile pictures)
├── requirements.txt         # Python dependencies
├── Procfile                 # Heroku/Render deployment config
├── runtime.txt              # Python version for Render deployment
├── docker-compose.yml       # Local PostgreSQL + pgAdmin setup
└── manage.py                # Django management command entry point
```

---

## 5. Database Models

All models live in `core/models.py` and `accounts/models.py`. Here is a complete breakdown.

### `accounts/models.py`

#### `User` (Custom User Model)

```python
class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)  # email is the login identifier
    currency = ...  # USD, EUR, GBP, INR
    timezone = ...
    language = ...  # For i18n support
    theme = ...     # light / dark / auto — persisted in DB via AJAX
    profile_picture = ...
    phone_number = ...
    email_notifications = models.BooleanField(default=True)
    budget_alerts = models.BooleanField(default=True)
    ...
    USERNAME_FIELD = 'email'  # Login with email, not username
```

**Why a Custom User Model?**  
Django strongly recommends creating a custom user model at the **start** of a project. If you use the default `User` model and later need to add fields (like `currency`, `theme`, `phone_number`), this requires complex database migrations. By subclassing `AbstractUser` from day 1, we own the model and can add any fields we want freely.

**Why email login instead of username?**  
Users forget usernames. Everyone knows their email address. Email-based login is the modern standard (Google, Facebook, GitHub all do this). It also prevents duplicate accounts since emails are naturally unique.

#### `UserSession`

Tracks active user sessions with IP address and user-agent string for security auditing. If a user sees an unfamiliar login location, they can investigate.

---

### `core/models.py`

#### `Category`

```python
class Category(models.Model):
    name = ...
    type = ...        # 'expense' or 'income'
    color = ...       # Hex color for UI display (#4361ee)
    icon = ...        # Font Awesome class (fa-tag)
    user = ...        # NULL for predefined/global categories
    parent = ...      # Self-referential FK for sub-categories
    is_active = ...
```

- **`user = NULL`** means it's a **predefined** (system-wide) category visible to all users
- **`user = <User>`** means it's a **user-created** custom category
- **`parent`** field supports **sub-categories** (e.g., "Food" → "Restaurants", "Groceries")
- **`unique_together = ['name', 'type', 'user']`** prevents duplicate categories per user

#### `PaymentMethod`

```python
class PaymentMethod(models.Model):
    name = ...         # "Credit Card", "Cash", "UPI"
    icon = ...
    user = ...
    is_default = ...   # Only one default allowed per user
```

The `save()` method on `PaymentMethod` automatically de-selects other defaults when a new default is set — so you can't have two "default" payment methods accidentally.

#### `Expense` ⭐ (Core Model)

```python
class Expense(models.Model):
    user = ForeignKey(User)
    amount = DecimalField(max_digits=12, decimal_places=2)  # supports up to 9,999,999,999.99
    date = DateField()
    time = TimeField(null=True)           # optional precise time
    category = ForeignKey(Category)      # SET_NULL so deleting a category doesn't delete expenses
    payment_method = ForeignKey(...)     # SET_NULL — same reason
    description = TextField()
    receipt = ImageField(upload_to='receipts/%Y/%m/')  # auto-organized by year/month
    location = CharField()               # where the expense happened
    is_tax_deductible = BooleanField()   # for tax purposes
    recurrence = CharField(choices=['none','daily','weekly','monthly','yearly'])
    recurrence_end_date = DateField()    # when to stop auto-generating
    tags = TaggableManager()             # django-taggit for flexible tagging
```

**Why `DecimalField` and not `FloatField` for money?**  
`FloatField` uses IEEE 754 floating-point arithmetic, which has precision errors. For example, `0.1 + 0.2 = 0.30000000000000004` in float. For money, this is **unacceptable**. `DecimalField` maps to SQL `DECIMAL/NUMERIC` which is exact. Always use `DecimalField` for financial values.

**Why `on_delete=models.SET_NULL` for category/payment_method?**  
`CASCADE` would delete all expenses if a category is deleted. `SET_NULL` preserves the expense record — the money was still spent, we just lost the category label. This is the correct behavior for financial data.

#### `Income`

Similar structure to `Expense` but with a `source` field (e.g., "Salary", "Freelance"). Tracks money coming in.

#### `Budget` ⭐

```python
class Budget(models.Model):
    user, category, amount, period  # core fields
    alert_threshold = IntegerField(default=80)  # alert at 80% spent
    rollover = BooleanField()         # carry unspent budget to next period?
    
    @property
    def spent_amount(self):
        # Calculates real-time spending for this category in current period
        
    @property
    def spent_percentage(self):
        # What % of budget has been used
        
    @property
    def is_over_budget(self):
        return self.spent_amount > self.amount
    
    @property
    def is_near_limit(self):
        return self.spent_percentage >= self.alert_threshold
```

**Why properties instead of storing `spent_amount` in the DB?**  
Because `spent_amount` changes every time an expense is added. Storing it would require updating it on every expense add/edit/delete — complex and error-prone. Computing it dynamically from actual expense records is always accurate. The tradeoff is a database query each time it's accessed, which is acceptable at this scale.

**`unique_together = ['user', 'category', 'period']`**  
A user can only have one budget for "Food" per "monthly" period. Having two "monthly Food budgets" would be nonsensical.

#### `FinancialGoal`

```python
class FinancialGoal(models.Model):
    name, goal_type, target_amount, current_amount
    deadline = DateField(null=True)      # optional deadline
    priority = CharField()               # low / medium / high
    status = CharField()                 # not_started / in_progress / completed / on_hold
    
    @property
    def progress_percentage(self):
        return min((current_amount / target_amount) * 100, 100)
    
    @property
    def remaining_amount(self):
        return max(target_amount - current_amount, 0)
```

Goal types: `savings`, `debt`, `purchase`, `emergency`, `investment`, `other`

#### `Notification`

```python
class Notification(models.Model):
    user, title, message, type, is_read, link, created_at
```

Types: `budget_warning`, `budget_exceeded`, `goal_milestone`, `goal_completed`, `reminder`, `info`

Notifications are created programmatically (by the budget check logic) and shown in the UI via the navbar. Users can mark them as read or clear all.

---

## 6. Application Modules

### `accounts` App — Authentication & User Management

**What it handles:**
- User registration (email + password)
- Login / logout
- Password change & reset
- User profile editing (currency, timezone, theme, notifications preferences)
- Two-Factor Authentication (2FA) setup and verification
- Session tracking (`UserSession` model)

**Key files:**
- `views.py` — Standard auth views (login, register, profile)
- `views_2fa.py` — TOTP 2FA setup (shows QR code) and verification
- `signals.py` — Django signal that fires after user creation to set up defaults

**Flow:**
```
User visits /register → Fills email + password → Account created → 
Redirected to /dashboard → Can optionally enable 2FA at /accounts/2fa/setup/
```

---

### `core` App — Business Logic

This is the largest app — it contains everything related to financial tracking.

**What it handles:**
- Dashboard (overview of income, expenses, budgets, goals)
- Expense CRUD (Create, Read, Update, Delete)
- Income CRUD
- Budget CRUD with real-time progress tracking
- Financial Goal CRUD with progress
- Reports & Analytics (charts, trends, savings rate, export)
- Notifications (create, list, mark-read)
- AJAX Quick-Add expense (no page reload)
- Keyboard shortcuts (globally applied via JavaScript)

**How the Dashboard works:**
```python
# views.py → dashboard() function collects:
- Total income this month
- Total expenses this month  
- Net savings = income - expenses
- Savings rate % = (savings / income) * 100
- Budget status for all active budgets
- Recent 5 expenses
- Goal progress for all goals
- Unread notification count
```

---

### `api` App — REST API Layer

**What it handles:**
- All CRUD operations via REST endpoints (JSON in/out)
- JWT-based authentication (no cookies/sessions for API)
- Auto-generated Swagger documentation at `/api/schema/swagger-ui/`
- Data serialization with read-only computed fields (e.g., `spent_percentage`)

The API is designed for use by:
- A mobile app (React Native / Flutter) that doesn't use HTML templates
- Third-party integrations
- Developers testing/exploring the system

---

## 7. REST API Layer

### Authentication Flow

```
POST /api/auth/register/  →  { email, password, password2 }  →  creates user
POST /api/auth/login/     →  { email, password }  →  returns { access, refresh }
POST /api/auth/refresh/   →  { refresh }  →  returns new { access }
POST /api/auth/logout/    →  { refresh }  →  blacklists refresh token
GET  /api/auth/profile/   →  returns user details (requires Bearer token)
```

**Why JWT and not session cookies for the API?**  
Session cookies are tied to a browser and require hitting the same server to validate. JWT tokens are stateless — any server can validate them using the secret key. This makes the API usable from mobile apps, curl, Postman, or any frontend without CSRF complexity.

### Key Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET/POST | `/api/expenses/` | List all expenses / Create expense |
| GET/PUT/DELETE | `/api/expenses/<id>/` | Get / Update / Delete specific expense |
| GET/POST | `/api/income/` | List income / Create income entry |
| GET/POST | `/api/budgets/` | List budgets / Create budget |
| GET/POST | `/api/goals/` | List goals / Create goal |
| GET | `/api/dashboard/` | Dashboard summary (totals, recent items) |
| GET | `/api/stats/monthly/` | Monthly income/expense breakdown (for charts) |
| GET | `/api/export/csv/` | Export data as CSV |
| GET | `/api/export/pdf/` | Export data as PDF |
| GET | `/api/export/json/` | Export data as JSON |
| GET | `/api/schema/swagger-ui/` | Interactive Swagger documentation |

### Serializers — Why They Matter

Serializers translate Django model instances into JSON (and validate incoming JSON into model instances). Each serializer:
- **Exposes read-only computed fields** like `spent_percentage` and `progress_percentage` directly in the API response — no extra client-side calculation needed
- **Automatically sets `user`** from the request context so users can't set other users' data
- **Validates input** (e.g., `password == password2` in `RegisterSerializer`)

Example from `BudgetSerializer`:
```python
spent_amount = serializers.ReadOnlyField()      # from Budget.spent_amount property
spent_percentage = serializers.ReadOnlyField()  # from Budget.spent_percentage property
is_over_budget = serializers.ReadOnlyField()    # from Budget.is_over_budget property
```

---

## 8. Security Features

### 1. Two-Factor Authentication (2FA / TOTP)

- **Library:** `django-otp` with `otp_totp` plugin
- **Flow:** User enables 2FA → shown a QR code → scanned with Google Authenticator → enters 6-digit code to verify → 2FA activated
- **Why TOTP over SMS?** SMS 2FA is vulnerable to SIM-swapping attacks. TOTP (Time-based One-Time Password) generates codes entirely offline and is far more secure.
- **Middleware:** `OTPMiddleware` in `settings.py` marks `request.user` as "OTP verified" on each request after successful 2FA verification.

### 2. Rate Limiting

- **Library:** `django-ratelimit` (referenced in settings)
- **Behavior:** Caps login and registration attempts at **5 per minute per IP**
- **Why?** Prevents brute-force attacks where a bot tries thousands of passwords against an account.
- **Why not `fail2ban`?** `fail2ban` works at the infrastructure level and requires server access. Application-level rate limiting works anywhere including shared hosting.

### 3. CSRF Protection

- Django's built-in `CsrfViewMiddleware` is active on all non-API routes.
- Every form submission includes a `{% csrf_token %}` that Django validates.
- The API uses JWT (stateless) so CSRF isn't needed for API endpoints.

### 4. Secure HTTP Headers (Production)

```python
# In settings.py when DEBUG=False:
SECURE_SSL_REDIRECT = True       # Force HTTPS
SESSION_COOKIE_SECURE = True     # Session cookie only over HTTPS
CSRF_COOKIE_SECURE = True        # CSRF cookie only over HTTPS
SECURE_BROWSER_XSS_FILTER = True # XSS protection header
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'         # Prevent clickjacking in iframes
```

### 5. Password Validation

Django's built-in validators are active:
- `UserAttributeSimilarityValidator` — password can't be too similar to your email/name
- `MinimumLengthValidator` — minimum 8 characters
- `CommonPasswordValidator` — rejects passwords like "password123"
- `NumericPasswordValidator` — rejects all-number passwords

### 6. JWT Token Blacklisting

```python
SIMPLE_JWT = {
    'ROTATE_REFRESH_TOKENS': True,       # Each refresh issues a new refresh token
    'BLACKLIST_AFTER_ROTATION': True,    # Old refresh tokens are blacklisted
}
```

When a user logs out, their refresh token is **blacklisted in the database** — making it impossible to get new access tokens with the old refresh token.

---

## 9. Advanced Features

### Recurring Transactions

- Fields: `recurrence` (none/daily/weekly/monthly/yearly), `recurrence_end_date`
- Management command `process_recurring.py` finds all expenses/incomes with active recurrence and auto-creates new records for the current period
- This is typically run via **cron job** or **Windows Task Scheduler** daily

**Why a management command and not a background task?**  
Celery (background task queue) requires Redis + Celery worker — complex setup. For a personal finance app, running a scheduled script once a day via cron is simpler, more reliable, and sufficient.

### AJAX Quick-Add Expense

- A modal form accessible from any page
- Submits to `/expenses/quick-add/` via JavaScript `fetch()` without page reload
- Returns JSON success/error response
- Template: `templates/core/partials/quick_add_form.html`
- **Why?** Friction kills good habits. If adding an expense requires navigating away from what you're doing, people stop doing it. A modal keeps the workflow seamless.

### Dark Mode with Server-Side Persistence

- Toggle button in navbar
- When toggled, sends AJAX request to save `theme = 'dark'/'light'` on the `User` model
- On page load, the user's preference is applied via a CSS class on `<body>`
- **Why server-side instead of `localStorage`?** `localStorage` is browser-specific — it doesn't sync across devices. Saving to the database means your dark mode preference follows you to any device or browser.

### Keyboard Shortcuts

Global shortcuts registered via JavaScript on `base.html`:
- `n` → Opens Quick-Add Expense modal
- `/` → Focuses the search filter input
- `d` → Navigates to Dashboard
- `e` → Navigates to Expenses

**Why?** Power users and developers appreciate keyboard-driven navigation. It's a small feature that makes the app feel professional.

### Analytics & Reports

The Reports page includes:
- **12-month Income vs Expense bar chart** using Chart.js (data from server via template JSON)
- **Category breakdown** — pie chart of spending by category
- **Savings Rate** — `(income - expenses) / income * 100` expressed as a percentage
- **Export options** — CSV for spreadsheet use, JSON for developers, PDF for record-keeping

### Email Notifications

- Budget warning emails sent via `core/emails.py` using Django's email backend
- `send_summary_email.py` management command sends weekly financial summaries
- In development: `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'` — emails are printed to terminal (no SMTP setup needed)
- In production: switch to `django.core.mail.backends.smtp.EmailBackend` and set SMTP credentials in `.env`

---

## 10. URL Map

### Web Interface Routes

| URL | View | Description |
|-----|------|-------------|
| `/` | `home` | Landing page |
| `/dashboard/` | `dashboard` | Main financial dashboard |
| `/expenses/` | `expense_list` | List all expenses with filters |
| `/expenses/add/` | `expense_create` | Add new expense |
| `/expenses/<id>/edit/` | `expense_edit` | Edit expense |
| `/expenses/<id>/delete/` | `expense_delete` | Delete expense |
| `/expenses/bulk-delete/` | `expense_bulk_delete` | Delete multiple selected expenses |
| `/expenses/quick-add/` | `quick_add_expense` | AJAX quick-add (partial) |
| `/income/` | `income_list` | List all income |
| `/budgets/` | `budget_list` | List budgets with progress |
| `/goals/` | `goal_list` | Financial goals with progress bars |
| `/reports/` | `reports` | Analytics dashboard with charts |
| `/reports/export-csv/` | `export_csv` | Download CSV export |
| `/reports/export-pdf/` | `export_pdf` | Download PDF report |
| `/categories/` | `category_list` | Manage expense/income categories |
| `/payment-methods/` | `payment_method_list` | Manage payment methods |
| `/notifications/` | `notification_list` | View all notifications |
| `/accounts/login/` | `login` | Login page |
| `/accounts/register/` | `register` | Registration page |
| `/accounts/profile/` | `profile` | User profile settings |
| `/accounts/2fa/setup/` | `2fa_setup` | Enable / manage 2FA |

### API Routes (prefix: `/api/`)

| Method | URL | Description |
|--------|-----|-------------|
| POST | `auth/register/` | Create account (API) |
| POST | `auth/login/` | Get JWT tokens |
| POST | `auth/logout/` | Blacklist refresh token |
| POST | `auth/refresh/` | Refresh access token |
| GET/PUT | `auth/profile/` | View/update profile |
| GET/POST | `expenses/` | List / create expenses |
| GET/PUT/DELETE | `expenses/<id>/` | Single expense |
| GET/POST | `income/` | List / create income |
| GET/POST | `budgets/` | List / create budgets |
| GET/POST | `goals/` | List / create goals |
| GET | `dashboard/` | Dashboard summary data |
| GET | `stats/monthly/` | Monthly chart data |
| GET | `export/csv/` | CSV export |
| GET | `export/pdf/` | PDF export |
| GET | `export/json/` | JSON export |
| GET | `schema/swagger-ui/` | Swagger interactive docs |

---

## 11. Configuration

All sensitive settings are stored in `expense_tracker/.env` and loaded via `python-decouple`.

### `.env` Variables

```bash
# Core
SECRET_KEY=your-very-long-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (leave empty for SQLite, set for PostgreSQL)
DATABASE_URL=postgres://user:password@localhost:5432/expense_tracker

# Email (for production SMTP)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=noreply@expensetracker.com
```

**Why `python-decouple` and not `os.environ`?**  
`decouple` reads from `.env` files in local development AND from real environment variables in production (Render, Heroku), transparently. It also supports type casting (`cast=bool`, `cast=int`) and default values — much cleaner than raw `os.environ.get()`.

**Why not keep `SECRET_KEY` in `settings.py`?**  
`settings.py` is committed to Git. If `SECRET_KEY` is in there, anyone with repo access can forge Django session cookies and bypass all authentication. It must be an environment variable.

---

## 12. Development Workflow

### Initial Setup

```bash
# 1. Clone the repository
git clone <repo-url>
cd expense-tracker

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create the .env file (copy from .env.example if available)
# Add SECRET_KEY, DEBUG=True, etc.

# 5. Run database migrations
python manage.py migrate

# 6. Seed default categories and payment methods
python manage.py seed_defaults

# 7. Create a superuser for Django Admin
python manage.py createsuperuser

# 8. Start the development server
python manage.py runserver
```

### Making Changes to Models

```bash
# After editing any model in models.py:
python manage.py makemigrations   # creates the migration file
python manage.py migrate          # applies it to the database
```

### Running Tests

```bash
python manage.py test
# or specific app:
python manage.py test accounts
python manage.py test core
```

### Using Docker for PostgreSQL (Local)

```bash
# Start PostgreSQL + pgAdmin
docker-compose up -d

# Access pgAdmin at http://localhost:5050
# Set DATABASE_URL=postgres://postgres:password@localhost:5432/expensedb in .env
```

---

## 13. Management Commands

Custom management commands live in `core/management/commands/`. Run them with:  
`python manage.py <command_name>`

### `process_recurring`

- **What it does:** Finds all `Expense` and `Income` records with `recurrence != 'none'` and where the recurrence is due (based on date and period). Creates new records for the current period.
- **When to run:** Daily, via cron on Linux (`0 0 * * * python manage.py process_recurring`) or Windows Task Scheduler
- **Why needed:** Users set a "Monthly Rent = ₹15,000" once, and every month it auto-appears in their expenses, keeping the dashboard accurate without manual entry.

### `send_summary_email`

- **What it does:** For each user who has `email_notifications=True`, calculates their weekly income/expense totals and sends a formatted summary email.
- **When to run:** Weekly, every Monday morning via cron
- **Why needed:** Passive awareness. Users who don't visit the app daily still get a weekly nudge about their financial health.

### `seed_defaults`

- **What it does:** Creates the default system-level categories (Food, Transport, Utilities, Entertainment, Healthcare, etc.) and payment methods (Cash, Credit Card, Debit Card, UPI) that are available to all users.
- **When to run:** Once, during initial setup
- **Why needed:** A fresh installation has no categories. Without seeding, users would have to create every category from scratch before they can add any expense.

---

## 14. Testing Strategy

Tests are written using Django's built-in `unittest`-based test framework.

### What's Tested (`accounts` and `core` apps)

1. **Auth Redirection** — Unauthenticated users are redirected to `/login/` when accessing protected pages
2. **User Session State** — Login succeeds with correct credentials, fails with wrong ones
3. **Budget Calculations** — `spent_amount`, `spent_percentage`, `is_over_budget` properties return correct values
4. **Model Validations** — `MinValueValidator(0.01)` on `amount` field rejects zero/negative amounts
5. **AJAX Quick-Add** — The quick-add endpoint returns JSON, handles invalid data gracefully
6. **Category Uniqueness** — Duplicate category names per user are rejected by the DB constraint
7. **Goal Progress** — `progress_percentage` calculates correctly with various current/target amounts

### Running Tests

```bash
python manage.py test                   # run all tests
python manage.py test accounts.tests   # run only accounts tests
python manage.py test --verbosity=2    # see each test name as it runs
```

### Test Result

```
Ran 9 tests in 15.423s
OK
```

---

## 15. Deployment

### Platform: Render (Backend)

The app is deployed on [Render](https://render.com) as a **Web Service**.

**Key configuration files:**

**`Procfile`:**
```
web: gunicorn expense_tracker.wsgi:application
```

**`runtime.txt`:**
```
python-3.12.0
```

**Environment Variables set on Render:**
- `SECRET_KEY` — unique production key
- `DEBUG=False`
- `DATABASE_URL` — PostgreSQL connection string from Render's DB
- `ALLOWED_HOSTS` — your render domain (e.g., `myapp.onrender.com`)
- `EMAIL_*` variables for SMTP

**Build Command on Render:**
```bash
pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --no-input
```

### Static Files in Production

WhiteNoise serves static files directly from Django without needing Nginx:
```python
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```
`python manage.py collectstatic` gathers all static files into `staticfiles/` which WhiteNoise then serves.

---

## 16. Design Decisions — Why NOT Something Else

### Why not React / Vue for the frontend?

This project uses Django's **server-side template rendering** (HTML templates). This decision was made because:
- **Simpler stack** — no separate Node.js build process, no CORS configuration, no separate deployment
- **DRF is still there** for anyone who wants to build a React frontend — the API fully exists
- For a financial tracking app where data is king, server-rendered HTML is fast and SEO-friendly
- Django templates with HTMX or vanilla AJAX (which we use for quick-add and dark-mode toggle) provide most of the interactivity needed

### Why not Flask?

Flask is micro-framework — great for small APIs but would require manually adding: ORM (SQLAlchemy), migrations (Alembic), auth, admin, forms, templating config, CSRF, sessions. Django gives all of this in one coherent package. For an app with this many models and features, Django is the right tool.

### Why not use SQLite in production?

SQLite is a **file-based** database. On Render/Heroku, the filesystem is **ephemeral** — it gets wiped on each deploy. All data would be lost. PostgreSQL is a proper server-based database that persists data independently of application deploys.

### Why `django-allauth` instead of writing custom auth?

Writing your own authentication is extremely risky — it's easy to make mistakes in password hashing, secure token generation, or email verification flows that lead to security vulnerabilities. `django-allauth` is battle-tested, maintained by the community, and handles all these edge cases correctly.

### Why not store reports data in a cache?

Report data (monthly totals for charts) is computed fresh on each page load from the database. For a personal app with one user's data, this is fast enough. Adding Redis caching would be premature optimization — it adds operational complexity for a problem that doesn't exist at this scale.

### Why `drf-spectacular` over `drf-yasg`?

`drf-yasg` generates OpenAPI 2.0 (Swagger 2.0). `drf-spectacular` generates **OpenAPI 3.0** which is the current standard and supports more features (responses, request bodies, etc.). `drf-spectacular` is also more actively maintained.

---

## 17. Common Questions & Answers

**Q: How do I add a new category?**  
A: Go to `/categories/add/` in the web UI, or `POST /api/categories/` in the API. Categories have a `type` field — make sure to set it to `expense` or `income`.

**Q: How does the Budget progress work?**  
A: The `Budget.spent_amount` property runs a live database query that sums all expenses in that category for the current period (week/month/year). It's not stored — it's always computed fresh from real transactions.

**Q: Can two users see each other's data?**  
A: No. Every query is filtered by `user=request.user`. Category querying uses `Q(user=request.user) | Q(user=None)` to include both personal and predefined categories. There is no way for one user to access another's data through the normal application flow.

**Q: How do I reset the database?**  
A: Delete `db.sqlite3`, then run `python manage.py migrate` and `python manage.py seed_defaults`.

**Q: How do I access the Django Admin?**  
A: Visit `/admin/` and log in with your superuser account. All models are registered and manageable from there.

**Q: How do I test the API?**  
A: Visit `/api/schema/swagger-ui/` for an interactive Swagger UI where you can execute API calls directly in the browser. Alternatively, use Postman — first POST to `/api/auth/login/` to get a JWT token, then add `Authorization: Bearer <token>` header to subsequent requests.

**Q: What happens if a category is deleted?**  
A: Expenses and income records that referenced that category have their `category` field set to `NULL` (`on_delete=SET_NULL`). The amount and date data is preserved — you just lose the category label.

**Q: How are recurring transactions created?**  
A: By running `python manage.py process_recurring`. In production, schedule this command to run daily. It reads the `recurrence` field and `recurrence_end_date` on each expense/income and creates new records accordingly.

**Q: Why does dark mode persist after logout and re-login?**  
A: Because `theme = 'dark'` is saved on the `User` model in the database (not in localStorage or cookies). When you log in again, the server reads your `theme` preference and applies it to the HTML.

---

## Appendix: Data Model Relationships

```
User (accounts.User)
 ├── Expense (core.Expense) [many]
 │    ├── Category [FK → core.Category]
 │    └── PaymentMethod [FK → core.PaymentMethod]
 ├── Income (core.Income) [many]
 │    └── Category [FK → core.Category]
 ├── Budget (core.Budget) [many]
 │    └── Category [FK → core.Category]
 ├── FinancialGoal (core.FinancialGoal) [many]
 ├── Notification (core.Notification) [many]
 ├── Category (core.Category) [many — user-created custom categories]
 ├── PaymentMethod (core.PaymentMethod) [many]
 └── UserSession (accounts.UserSession) [many]

Category
 └── Category (self) [FK → parent, for sub-categories]
```

---

*Last updated: March 2026 — covers the complete state of the project including all features through v1.0.*
