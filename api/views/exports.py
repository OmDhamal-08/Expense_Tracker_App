import csv
import json
from datetime import date
from decimal import Decimal
from io import BytesIO

from django.db.models import Sum
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import permissions
from rest_framework.views import APIView

from core.models import Expense, Income


CURRENCY_SYMBOLS = {'USD': '$', 'EUR': '€', 'GBP': '£', 'INR': 'Rs.'}


def _get_date_range(request):
    """Helper: parse date_from / date_to from query params with sensible defaults."""
    today = date.today()
    date_from = request.query_params.get('date_from') or today.replace(day=1).isoformat()
    date_to = request.query_params.get('date_to') or today.isoformat()
    return date_from, date_to


class ExportCSVView(APIView):
    """
    GET /api/export/csv/?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD
    Returns a CSV file of all expenses and income for the given period.
    Defaults to the current month if no dates are given.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        date_from, date_to = _get_date_range(request)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="report_{date_from}_to_{date_to}.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Date', 'Type', 'Category', 'Amount',
            'Description', 'Payment Method', 'Location', 'Tax Deductible',
        ])

        expenses = Expense.objects.filter(
            user=user, date__gte=date_from, date__lte=date_to
        ).select_related('category', 'payment_method').order_by('-date')

        for e in expenses:
            writer.writerow([
                e.date, 'Expense',
                e.category.name if e.category else '',
                e.amount, e.description,
                e.payment_method.name if e.payment_method else '',
                e.location,
                'Yes' if e.is_tax_deductible else 'No',
            ])

        incomes = Income.objects.filter(
            user=user, date__gte=date_from, date__lte=date_to
        ).select_related('category').order_by('-date')

        for i in incomes:
            writer.writerow([
                i.date, 'Income',
                i.category.name if i.category else '',
                i.amount, i.description, '', '', '',
            ])

        return response


class ExportPDFView(APIView):
    """
    GET /api/export/pdf/?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD
    Returns a PDF financial report for the given period.
    Defaults to the current month if no dates are given.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from django.template.loader import render_to_string
        from xhtml2pdf import pisa

        user = request.user
        date_from, date_to = _get_date_range(request)

        expenses = Expense.objects.filter(
            user=user, date__gte=date_from, date__lte=date_to
        ).select_related('category', 'payment_method').order_by('-date')

        incomes = Income.objects.filter(
            user=user, date__gte=date_from, date__lte=date_to
        ).select_related('category').order_by('-date')

        total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        total_income = incomes.aggregate(total=Sum('amount'))['total'] or Decimal('0')

        category_breakdown = expenses.values(
            'category__name', 'category__color'
        ).annotate(total=Sum('amount')).order_by('-total')

        sym = CURRENCY_SYMBOLS.get(user.currency, '$')

        html = render_to_string('core/reports/pdf_report.html', {
            'user': user,
            'date_from': date_from,
            'date_to': date_to,
            'expenses': expenses,
            'incomes': incomes,
            'total_expenses': total_expenses,
            'total_income': total_income,
            'net': total_income - total_expenses,
            'category_breakdown': category_breakdown,
            'sym': sym,
        })

        result = BytesIO()
        pdf = pisa.CreatePDF(BytesIO(html.encode('utf-8')), dest=result, encoding='utf-8')

        if pdf.err:
            return HttpResponse('PDF generation failed.', status=500)

        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="report_{date_from}_to_{date_to}.pdf"'
        return response


class ExportJSONView(APIView):
    """
    GET /api/export/json/?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD
    Returns a structured JSON export of all financial data.
    Defaults to the current month if no dates are given.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        date_from, date_to = _get_date_range(request)

        expenses = Expense.objects.filter(
            user=user, date__gte=date_from, date__lte=date_to
        ).select_related('category', 'payment_method').order_by('-date')

        incomes = Income.objects.filter(
            user=user, date__gte=date_from, date__lte=date_to
        ).select_related('category').order_by('-date')

        total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        total_income = incomes.aggregate(total=Sum('amount'))['total'] or Decimal('0')

        data = {
            'period': {'from': date_from, 'to': date_to},
            'summary': {
                'total_income': str(total_income),
                'total_expenses': str(total_expenses),
                'net': str(total_income - total_expenses),
                'currency': user.currency,
            },
            'expenses': [
                {
                    'date': e.date.isoformat(),
                    'amount': str(e.amount),
                    'category': e.category.name if e.category else None,
                    'payment_method': e.payment_method.name if e.payment_method else None,
                    'description': e.description,
                    'location': e.location,
                    'is_tax_deductible': e.is_tax_deductible,
                }
                for e in expenses
            ],
            'income': [
                {
                    'date': i.date.isoformat(),
                    'amount': str(i.amount),
                    'source': i.source,
                    'category': i.category.name if i.category else None,
                    'description': i.description,
                }
                for i in incomes
            ],
        }

        response = HttpResponse(
            json.dumps(data, indent=2, default=str),
            content_type='application/json',
        )
        response['Content-Disposition'] = f'attachment; filename="report_{date_from}_to_{date_to}.json"'
        return response
