"""
AI-powered spending insights using Google Gemini API.

Collects the user's financial data (expenses, income, budgets, goals)
and sends a structured prompt to Gemini for personalised analysis.
"""
import json
from datetime import timedelta
from decimal import Decimal

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from core.models import Budget, Category, Expense, FinancialGoal, Income


# ── Gemini API helper ──────────────────────────────────────────────────

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


def _build_financial_summary(user):
    """Aggregate the user's financial data into a dict for the prompt."""
    today = timezone.now().date()
    month_start = today.replace(day=1)

    # Current month
    month_expenses = (
        Expense.objects.filter(user=user, date__gte=month_start, date__lte=today)
        .values("category__name")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )
    month_income = (
        Income.objects.filter(user=user, date__gte=month_start, date__lte=today)
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0")
    )
    month_expense_total = (
        Expense.objects.filter(user=user, date__gte=month_start, date__lte=today)
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0")
    )

    # Previous month
    prev_end = month_start - timedelta(days=1)
    prev_start = prev_end.replace(day=1)
    prev_expense_total = (
        Expense.objects.filter(user=user, date__gte=prev_start, date__lte=prev_end)
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0")
    )
    prev_income_total = (
        Income.objects.filter(user=user, date__gte=prev_start, date__lte=prev_end)
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0")
    )

    # Budgets
    budgets = []
    for b in Budget.objects.filter(user=user, is_active=True).select_related("category"):
        budgets.append({
            "category": b.category.name,
            "limit": float(b.amount),
            "spent": float(b.spent_amount),
            "percent_used": float(b.spent_percentage),
        })

    # Goals
    goals = []
    for g in FinancialGoal.objects.filter(user=user).exclude(status="completed"):
        goals.append({
            "name": g.name,
            "target": float(g.target_amount),
            "saved": float(g.current_amount),
            "progress": float(g.progress_percentage),
            "deadline": g.deadline.isoformat() if g.deadline else None,
        })

    # Top spending categories (last 3 months)
    three_months_ago = today - timedelta(days=90)
    top_categories = list(
        Expense.objects.filter(user=user, date__gte=three_months_ago)
        .values("category__name")
        .annotate(total=Sum("amount"))
        .order_by("-total")[:6]
    )

    return {
        "currency": user.currency,
        "current_month": {
            "income": float(month_income),
            "expenses": float(month_expense_total),
            "savings": float(month_income - month_expense_total),
            "category_breakdown": [
                {"category": e["category__name"], "amount": float(e["total"])}
                for e in month_expenses
            ],
        },
        "previous_month": {
            "income": float(prev_income_total),
            "expenses": float(prev_expense_total),
        },
        "budgets": budgets,
        "active_goals": goals,
        "top_spending_3mo": [
            {"category": c["category__name"], "amount": float(c["total"])}
            for c in top_categories
        ],
    }


def _call_gemini(api_key, financial_data):
    """Call Google Gemini API and return the text response."""
    prompt = f"""You are a friendly, expert personal finance advisor. Analyze the following
financial data and provide actionable, personalized insights.

FINANCIAL DATA (JSON):
{json.dumps(financial_data, indent=2)}

Respond in well-structured Markdown with these sections:
## Monthly Overview
A brief 2-3 sentence summary of this month's finances.

## Key Insights
- 3-4 bullet points: spending trends, budget adherence, notable changes vs last month.

## Savings Tips
- 2-3 specific, actionable tips based on their actual spending patterns.

## Goal Progress
- Comment on each active goal — are they on track? What should they adjust?

## Risk Alerts
- Any budgets near limit or overspent? Any concerning trends?

Keep response concise (under 400 words). Use {financial_data.get('currency', 'USD')} currency symbols.
Be encouraging but honest. Use simple language.
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1024,
        },
    }

    response = requests.post(
        f"{GEMINI_API_URL}?key={api_key}",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30,
    )

    if response.status_code != 200:
        raise Exception(f"Gemini API error {response.status_code}: {response.text[:300]}")

    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


# ── Views ──────────────────────────────────────────────────────────────

@login_required
def insights_view(request):
    """Render the AI insights page."""
    return render(request, "core/insights.html")


@login_required
def insights_api(request):
    """
    AJAX endpoint: generate AI insights for the logged-in user.
    Returns JSON: { "insights": "<markdown string>" } or { "error": "..." }
    """
    api_key = getattr(settings, "GEMINI_API_KEY", "")
    if not api_key:
        return JsonResponse(
            {"error": "Gemini API key not configured. Add GEMINI_API_KEY to your .env file."},
            status=503,
        )

    try:
        summary = _build_financial_summary(request.user)
        markdown = _call_gemini(api_key, summary)
        return JsonResponse({"insights": markdown})
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=500)
