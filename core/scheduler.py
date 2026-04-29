"""
Scheduled jobs using django-apscheduler.
Jobs are registered once when the Django app starts (via CoreConfig.ready()).

Jobs:
    - process_recurring : daily at 00:01 UTC — auto-generates recurring transactions
    - send_summary_email: every Monday at 08:00 UTC — weekly email digests
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django.core.management import call_command

logger = logging.getLogger(__name__)


def process_recurring_job():
    """Auto-generate recurring expense / income for today."""
    logger.info("Running scheduled job: process_recurring")
    call_command("process_recurring")


def send_summary_email_job():
    """Send weekly expense summary emails to opted-in users."""
    logger.info("Running scheduled job: send_summary_email")
    call_command("send_summary_email")


def start():
    """
    Start the APScheduler background scheduler.
    Called once from CoreConfig.ready() so jobs are never registered twice.
    """
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # ── Job 1: Process Recurring Transactions ─────────────────────────────────
    scheduler.add_job(
        process_recurring_job,
        trigger=CronTrigger(hour=0, minute=1),   # daily at 00:01 UTC
        id="process_recurring",
        name="Process Recurring Transactions",
        replace_existing=True,
    )

    # ── Job 2: Weekly Summary Email ────────────────────────────────────────────
    scheduler.add_job(
        send_summary_email_job,
        trigger=CronTrigger(day_of_week="mon", hour=8, minute=0),  # Monday 08:00 UTC
        id="send_summary_email",
        name="Send Weekly Summary Email",
        replace_existing=True,
    )

    logger.info("APScheduler started — recurring & email jobs registered.")
    scheduler.start()
