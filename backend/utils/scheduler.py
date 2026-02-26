"""
SCHEDULER UTILITIES FOR PULSE
==============================

The main scheduling logic lives in tasks.py using Celery Beat.
This module provides helper functions for scheduler-related operations.

HOW CELERY BEAT WORKS:
    Celery Beat is a separate process that acts like a cron daemon.
    It reads the beat_schedule config from tasks.py and, at the
    specified intervals, pushes task messages to Redis.

    A Celery worker then picks up those messages and executes them.

    You need THREE processes running:
    1. Redis server        — the message queue
    2. Celery worker       — executes tasks
    3. Celery beat         — schedules periodic tasks

STARTING THE SCHEDULER:
    cd backend/

    # Start Redis (if not already running via Docker or brew)
    redis-server

    # Start the Celery worker
    celery -A tasks worker --loglevel=info

    # Start Celery Beat (the scheduler)
    celery -A tasks beat --loglevel=info

USEFUL CELERY CLI COMMANDS:
    # Inspect active tasks
    celery -A tasks inspect active

    # Inspect scheduled tasks
    celery -A tasks inspect scheduled

    # Inspect registered tasks
    celery -A tasks inspect registered

    # Purge all pending tasks from the queue
    celery -A tasks purge
"""


def get_due_reminder_count():
    """Helper to check how many reminders are due and pending."""
    from models.reminder import Reminder
    from datetime import date

    return Reminder.query.filter(
        Reminder.scheduled_date <= date.today(),
        Reminder.status == 'pending'
    ).count()
