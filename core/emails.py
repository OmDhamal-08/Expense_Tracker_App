"""
#6  Real email notifications helper.
#7  Weekly / monthly summary email helper.
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


def send_budget_alert_email(user, budget, alert_type='warning'):
    """Send a budget warning or exceeded email to the user."""
    if not user.email_notifications or not user.budget_alerts:
        return
    subject = (
        f'Budget Exceeded: {budget.category.name}'
        if alert_type == 'exceeded'
        else f'Budget Warning: {budget.category.name}'
    )
    message = render_to_string('core/emails/budget_alert.txt', {
        'user': user,
        'budget': budget,
        'alert_type': alert_type,
    })
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )


def send_goal_milestone_email(user, goal, milestone='50%'):
    """Send a goal milestone or completion email."""
    if not user.email_notifications:
        return
    subject = (
        f'Goal Completed: {goal.name}'
        if milestone == 'completed'
        else f'Goal Milestone ({milestone}): {goal.name}'
    )
    message = render_to_string('core/emails/goal_milestone.txt', {
        'user': user,
        'goal': goal,
        'milestone': milestone,
    })
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )


def send_weekly_summary_email(user, summary_data):
    """#7 Send weekly summary email."""
    if not user.email_notifications:
        return
    subject = 'Your Weekly Expense Summary'
    message = render_to_string('core/emails/weekly_summary.txt', {
        'user': user,
        **summary_data,
    })
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )
