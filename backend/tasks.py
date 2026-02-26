"""
CELERY TASK DEFINITIONS FOR PULSE
==================================

What is Celery?
    Celery is a distributed task queue for Python. It lets you run functions
    asynchronously (in the background) instead of blocking your Flask request.
    When you call `send_reminder.delay(to, msg)`, the function doesn't run
    right away — instead, a message is placed on a Redis queue, and a separate
    Celery worker process picks it up and executes it.

What is Redis?
    Redis is an in-memory data store. In this project, it serves as the
    "message broker" — the middleman between your Flask app and the Celery
    worker. Think of it like a mailbox: Flask drops a letter (task message)
    into the mailbox, and the Celery worker checks the mailbox and processes it.

How they work together in Pulse:
    1. Flask API receives a request (e.g., "send this reminder")
    2. Flask calls send_reminder.delay(phone, message)
       - .delay() serializes the function name + arguments as JSON
       - Sends that JSON to Redis (the broker)
    3. A Celery worker process is listening on Redis
       - It picks up the message
       - Deserializes it and calls send_reminder(phone, message)
       - The actual Twilio SMS/WhatsApp call happens here
    4. The result (success/failure) is stored back in Redis (the backend)

Running locally:
    # Terminal 1: Start Redis (if not already running)
    redis-server

    # Terminal 2: Start the Celery worker (from the backend/ directory)
    celery -A tasks worker --loglevel=info

    # Terminal 3: Start Celery Beat for scheduled tasks
    celery -A tasks beat --loglevel=info

    # Terminal 4: Start Flask
    python app.py
"""

from utils.twilio_client import send_sms
from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------
# CELERY CONFIGURATION
# ---------------------------------------------------------------
# The Celery instance needs two URLs:
#   broker  = where task messages are queued (Redis)
#   backend = where task results are stored (also Redis)
# ---------------------------------------------------------------
celery = Celery('tasks', broker=os.getenv('REDIS_URL'), backend=os.getenv('REDIS_URL'))

# ---------------------------------------------------------------
# CELERY BEAT SCHEDULE
# ---------------------------------------------------------------
# Celery Beat is a scheduler that runs as a separate process.
# It periodically pushes task messages onto the Redis queue
# according to this schedule.
#
# crontab(minute=0, hour=8)  = every day at 8:00 AM
# crontab(minute='*/15')     = every 15 minutes
# crontab()                  = every minute (for testing)
# ---------------------------------------------------------------
celery.conf.beat_schedule = {
    'check-reminders-daily': {
        'task': 'tasks.check_and_send_reminders',
        'schedule': crontab(minute=0, hour=8),  # Every day at 8 AM
    },
}
celery.conf.timezone = 'UTC'


@celery.task
def send_reminder(to, message):
    """
    Send a single reminder message using Twilio.

    This is called two ways:
      1. Directly via .delay() when a user clicks "Send Now" in the dashboard
      2. By check_and_send_reminders() for scheduled reminders

    The difference between:
      send_reminder(to, msg)        — runs synchronously (blocks)
      send_reminder.delay(to, msg)  — runs asynchronously (queued in Redis)
      send_reminder.apply_async(args=[to, msg], countdown=60)  — runs async after 60s delay
    """
    return send_sms(to, message)


@celery.task
def check_and_send_reminders():
    """
    Periodic task: query the database for all reminders that are due today
    (or overdue) and still pending. For each one, dispatch a send_reminder
    task and update the status to 'sent'.

    This task needs Flask's app context because it uses SQLAlchemy to
    query the database.
    """
    from app import app
    from models.reminder import Reminder
    from models.task_event import TaskEvent
    from models import db
    from datetime import date, datetime, timezone

    with app.app_context():
        due_reminders = Reminder.query.filter(
            Reminder.scheduled_date <= date.today(),
            Reminder.status == 'pending'
        ).all()

        sent_count = 0
        for reminder in due_reminders:
            worker = reminder.assigned_worker
            if worker and worker.phone:
                # .delay() queues this as a separate async task
                send_reminder.delay(worker.phone, reminder.message)
                reminder.status = 'sent'
                reminder.sent_at = datetime.now(timezone.utc)

                event = TaskEvent(
                    reminder_id=reminder.id,
                    worker_id=worker.id,
                    event_type='sent'
                )
                db.session.add(event)
                sent_count += 1

        db.session.commit()
        return f'Processed {sent_count} of {len(due_reminders)} due reminders'
