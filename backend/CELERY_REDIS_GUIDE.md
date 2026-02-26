# Celery & Redis in Pulse -- A Friendly Guide

> **Audience:** You are new to Celery and Redis and want to understand how they
> power the background task system in **Pulse**, a Flask-based WhatsApp reminder
> bot for fleet management.

---

## Table of Contents

1. [What is Redis?](#1-what-is-redis)
2. [What is Celery?](#2-what-is-celery)
3. [How They Work Together in Pulse](#3-how-they-work-together-in-pulse)
4. [Celery Beat (Periodic Scheduler)](#4-celery-beat-periodic-scheduler)
5. [Key Celery Concepts](#5-key-celery-concepts)
6. [Step-by-Step Local Setup](#6-step-by-step-local-setup)
7. [Useful Debugging Commands](#7-useful-debugging-commands)
8. [Code Walkthrough of tasks.py](#8-code-walkthrough-of-taskspy)

---

## 1. What is Redis?

**Redis** (Remote Dictionary Server) is an **in-memory data structure store**. It
keeps all of its data in RAM, which makes it *extremely* fast -- we are talking
microsecond response times.

### What can Redis do?

| Capability | Plain-English Explanation |
|---|---|
| **Key-value store** | Store and retrieve data by a unique key, like a Python dictionary. |
| **Pub/Sub messaging** | Publish messages to channels; subscribers receive them instantly. |
| **Queues (Lists)** | Push items onto a list and pop them off the other end -- a perfect queue. |
| **Expiring keys** | Set a TTL (time-to-live) so data auto-deletes after N seconds. |

### How Pulse uses Redis

In Pulse, Redis plays **two roles**:

1. **Message broker** -- It holds the queue of tasks that Flask wants Celery to
   process. When Flask says "send this WhatsApp reminder", the message sits in a
   Redis list until a Celery worker picks it up.
2. **Result backend** -- After a Celery worker finishes a task, it stores the
   result (success, failure, return value) back in Redis so you can check on it
   later.

### The Mailbox Analogy

Think of Redis as a **super-fast mailbox** sitting between your Flask app and
your Celery workers:

```
You (Flask) write a letter    -->  Drop it in the mailbox (Redis)
                                        |
The mail carrier (Celery)     <--  Picks it up and delivers it
```

Flask never has to wait for the delivery to finish. It drops the letter and
moves on to handle the next web request.

---

## 2. What is Celery?

**Celery** is a **distributed task queue** for Python. It lets you take any
Python function and run it **asynchronously** -- meaning "in the background,
outside of your web request."

### Why do we need it?

Imagine a user clicks "Send Reminder" in the Pulse dashboard. Without Celery,
your Flask route would have to:

1. Call the Twilio API (which might take 1-3 seconds).
2. Wait for a response.
3. Only *then* return a response to the browser.

The user stares at a loading spinner the whole time. If Twilio is slow or the
network hiccups, the request might even time out.

With Celery, the Flask route instead says: "Hey Celery, send this reminder for
me," and **immediately** returns a response to the user. The actual Twilio call
happens in a separate **worker process** a moment later.

### Core pieces of Celery

| Piece | What it does |
|---|---|
| **Celery app** | The main Celery instance that knows your configuration and tasks. |
| **Worker** | A separate process that listens for tasks and executes them. |
| **Beat** | A scheduler process that periodically pushes tasks onto the queue. |
| **Broker** | The transport layer (Redis, in our case) that carries task messages. |
| **Backend** | Where task results are stored (also Redis, in our case). |

---

## 3. How They Work Together in Pulse

Here is the full picture, from a user clicking a button to a WhatsApp message
being delivered:

```
                         PULSE ARCHITECTURE
                         ==================

  [Browser / React Frontend]
           |
           |  POST /api/reminders/5/send
           v
  +------------------+
  |   Flask API      |   <-- routes/reminders.py: send_reminder_now()
  |   (app.py)       |
  +--------+---------+
           |
           |  send_reminder.delay(phone, message)
           |  (puts a JSON message onto the Redis queue)
           v
  +------------------+
  |     Redis        |   <-- message broker (redis://localhost:6379)
  |  (task queue)    |
  +--------+---------+
           |
           |  Celery worker picks up the message
           v
  +------------------+
  |  Celery Worker   |   <-- tasks.py: send_reminder()
  |  (background)    |
  +--------+---------+
           |
           |  Calls Twilio API
           v
  +------------------+
  |     Twilio       |   <-- utils/twilio_client.py: send_sms()
  +--------+---------+
           |
           v
  +------------------+
  |    WhatsApp      |   <-- Worker receives the message on their phone
  +------------------+
```

### Step by step

1. A user clicks "Send Now" on a reminder in the React dashboard.
2. The browser sends `POST /api/reminders/5/send` to the Flask API.
3. The Flask route (`routes/reminders.py` -- `send_reminder_now()`) looks up the
   reminder and its assigned worker, then calls:
   ```python
   from tasks import send_reminder
   send_reminder.delay(worker.phone, reminder.message)
   ```
4. `.delay()` serializes the function name and arguments as JSON and pushes that
   message into a **Redis list** (the queue).
5. Flask immediately returns `{"message": "Reminder sent successfully"}` to the
   browser. The user sees instant feedback.
6. Meanwhile, in a separate terminal, a **Celery worker** is running. It is
   constantly polling Redis for new messages.
7. The worker picks up the message, deserializes it, and calls
   `send_reminder(worker.phone, reminder.message)`.
8. Inside that function, `send_sms()` from `utils/twilio_client.py` calls the
   Twilio API, which delivers the WhatsApp message to the worker's phone.
9. The task result (the Twilio message SID, or an error) is stored back in Redis.

---

## 4. Celery Beat (Periodic Scheduler)

Celery Beat is a **scheduler** that runs as its own process. Its job is to push
tasks onto the Redis queue at specific times -- like a cron job, but built right
into Celery.

### The beat_schedule in Pulse

In `tasks.py`, you will find this configuration:

```python
celery.conf.beat_schedule = {
    'check-reminders-daily': {
        'task': 'tasks.check_and_send_reminders',
        'schedule': crontab(minute=0, hour=8),  # Every day at 8 AM
    },
}
celery.conf.timezone = 'UTC'
```

Let's break that down:

| Key | Value | Meaning |
|---|---|---|
| `'check-reminders-daily'` | (name) | A human-readable name for this schedule entry. |
| `'task'` | `'tasks.check_and_send_reminders'` | The full dotted path to the task function. |
| `'schedule'` | `crontab(minute=0, hour=8)` | Run at 8:00 AM UTC every day. |

### How crontab() works

`crontab()` follows the same logic as Unix cron expressions. Here are some
useful examples:

```python
from celery.schedules import crontab

# Every day at 8:00 AM (what Pulse uses)
crontab(minute=0, hour=8)

# Every Monday at 7:30 AM
crontab(minute=30, hour=7, day_of_week=1)

# Every 15 minutes
crontab(minute='*/15')

# Every minute (useful for testing)
crontab()

# First day of every month at midnight
crontab(minute=0, hour=0, day_of_month=1)

# Weekdays only at 9 AM
crontab(minute=0, hour=9, day_of_week='1-5')
```

### What happens at 8 AM every day

1. Celery Beat wakes up and sees it is time for `check-reminders-daily`.
2. Beat pushes a `tasks.check_and_send_reminders` message onto the Redis queue.
3. A Celery worker picks it up and runs `check_and_send_reminders()`.
4. That function queries the database for all reminders that are due today (or
   overdue) and still have `status == 'pending'`.
5. For each one, it calls `send_reminder.delay(phone, message)` -- which itself
   is *another* async task that goes through Redis.
6. The reminder status is updated to `'sent'` and a `TaskEvent` is logged.

This two-level approach (Beat triggers a check, which spawns individual send
tasks) is a common Celery pattern. It keeps each task small and independently
retryable.

---

## 5. Key Celery Concepts

### The @celery.task decorator

This is how you turn a regular Python function into a Celery task:

```python
@celery.task
def send_reminder(to, message):
    return send_sms(to, message)
```

Behind the scenes, this decorator:
- Registers the function with Celery so workers know about it.
- Adds `.delay()`, `.apply_async()`, and other methods to the function.
- Wraps the function so its execution can be tracked (states, retries, etc.).

### .delay() vs .apply_async() vs direct call

There are three ways to invoke a Celery task. This is a critical distinction:

```python
# 1. DIRECT CALL -- runs synchronously, RIGHT HERE, RIGHT NOW.
#    No Redis. No worker. Just a normal function call.
#    Useful for testing or when you do not need async.
result = send_reminder("+15551234567", "Oil change due")

# 2. .delay() -- runs asynchronously via Redis + worker.
#    This is the shortcut you will use 90% of the time.
#    It returns an AsyncResult immediately (not the actual result).
async_result = send_reminder.delay("+15551234567", "Oil change due")

# 3. .apply_async() -- runs asynchronously with extra options.
#    Use this when you need countdown, eta, retries, etc.
async_result = send_reminder.apply_async(
    args=["+15551234567", "Oil change due"],
    countdown=60,          # wait 60 seconds before running
    retry=True,            # retry on failure
    retry_policy={
        'max_retries': 3,
        'interval_start': 10,  # wait 10s before first retry
    }
)
```

Quick reference:

| Method | Async? | Goes through Redis? | Supports options? |
|---|---|---|---|
| `send_reminder(...)` | No | No | No |
| `send_reminder.delay(...)` | Yes | Yes | No (just args) |
| `send_reminder.apply_async(...)` | Yes | Yes | Yes (countdown, eta, retries, ...) |

### Task states

Every Celery task goes through a lifecycle of states:

```
  PENDING  -->  STARTED  -->  SUCCESS
                   |
                   +--->  FAILURE
                   |
                   +--->  RETRY
```

| State | Meaning |
|---|---|
| **PENDING** | The task has been sent to Redis but no worker has picked it up yet. |
| **STARTED** | A worker has started executing the task. (Only tracked if `task_track_started=True`.) |
| **SUCCESS** | The task completed without raising an exception. |
| **FAILURE** | The task raised an unhandled exception. |
| **RETRY** | The task failed but is scheduled to be retried. |
| **REVOKED** | The task was cancelled before or during execution. |

You can check a task's state using the `AsyncResult` object:

```python
result = send_reminder.delay("+15551234567", "Oil change due")

print(result.id)       # e.g. "a1b2c3d4-e5f6-..."
print(result.state)    # "PENDING", "SUCCESS", etc.
print(result.result)   # The return value (once SUCCESS) or the exception (once FAILURE)
print(result.ready())  # True if the task is finished (SUCCESS or FAILURE)
```

### Task retries

If a task fails (say, Twilio is temporarily down), you can tell Celery to retry
it automatically:

```python
@celery.task(bind=True, max_retries=3, default_retry_delay=60)
def send_reminder(self, to, message):
    try:
        return send_sms(to, message)
    except Exception as exc:
        # self.retry() re-queues the task with exponential backoff
        raise self.retry(exc=exc)
```

Key points about retries:
- `bind=True` gives the task access to `self`, which is the task instance.
- `max_retries=3` means it will try up to 3 more times after the first failure.
- `default_retry_delay=60` means it waits 60 seconds before each retry.
- `self.retry(exc=exc)` re-queues the task. The `exc` argument preserves the
  original traceback for logging.

---

## 6. Step-by-Step Local Setup

You need **four separate terminal windows** to run the full Pulse stack locally.
Here is exactly what to do:

### Prerequisites

Make sure you have these installed:
- Python 3.x
- Redis
- PostgreSQL (for the Pulse database)

### Terminal 1: Start Redis

```bash
# Install Redis (macOS with Homebrew)
brew install redis

# Start the Redis server
redis-server
```

You should see output like:
```
Ready to accept connections tcp
```

Redis is now listening on `localhost:6379`.

### Terminal 2: Start the Celery Worker

```bash
# Navigate to the backend directory
cd backend/

# Activate your virtual environment
source venv/bin/activate

# Start a Celery worker
celery -A tasks worker --loglevel=info
```

You should see output like:
```
[config]
.> app:         tasks:0x...
.> transport:   redis://localhost:6379//
.> results:     redis://localhost:6379//
.> concurrency: 8 (prefork)

[queues]
.> celery       exchange=celery(direct) key=celery

[tasks]
  . tasks.check_and_send_reminders
  . tasks.send_reminder

[... ready.]
```

The worker is now listening for tasks on the Redis queue.

### Terminal 3: Start Celery Beat

```bash
cd backend/
source venv/bin/activate

# Start the beat scheduler
celery -A tasks beat --loglevel=info
```

You should see:
```
celery beat v5.x.x is starting.
__    -    ... ...      -    _
LocalTime -> 2025-01-01 08:00:00
...
beat: Starting...
```

Beat is now running and will push `check_and_send_reminders` onto the queue
every day at 8:00 AM UTC.

### Terminal 4: Start Flask

```bash
cd backend/
source venv/bin/activate

# Start the Flask development server
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
```

### Quick sanity check

With all four processes running, you can test the full flow:

```bash
# Create a test reminder via the API, then trigger it:
curl -X POST http://localhost:5000/api/reminders/1/send
```

Watch Terminal 2 (the Celery worker) -- you should see it pick up and execute
the `send_reminder` task.

### Environment variables

Make sure your `.env` file includes:

```env
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=postgresql://localhost/whatsapp_bot
TWILIO_ACCOUNT_SID=your_sid_here
TWILIO_AUTH_TOKEN=your_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

---

## 7. Useful Debugging Commands

When things are not working, these commands are your best friends:

### Inspect active tasks (currently being executed by workers)

```bash
celery -A tasks inspect active
```

### Inspect scheduled tasks (waiting to run at a future time)

```bash
celery -A tasks inspect scheduled
```

### List all registered tasks (confirms your tasks are discovered)

```bash
celery -A tasks inspect registered
```

Expected output:
```
-> worker@hostname: OK
    * tasks.check_and_send_reminders
    * tasks.send_reminder
```

If your tasks are not listed here, the worker cannot see them.

### Purge all pending tasks (clear the queue -- use with caution!)

```bash
celery -A tasks purge
```

This deletes all messages from the Redis queue. Useful when you have a backlog
of broken tasks during development.

### Monitor Redis in real time

```bash
redis-cli MONITOR
```

This shows every command Redis receives in real time. You will see Celery
pushing and popping task messages. Very useful for understanding the flow, but
noisy in production.

Example output:
```
"LPUSH" "celery" "{\"body\": \"...\", \"headers\": {\"task\": \"tasks.send_reminder\", ...}}"
```

### Check the queue length

```bash
redis-cli LLEN celery
```

This tells you how many tasks are waiting in the queue. If this number keeps
growing, your workers are not keeping up.

```
(integer) 0    <-- queue is empty, workers are keeping up
(integer) 47   <-- 47 tasks waiting, you might need more workers
```

### Other helpful Redis CLI commands

```bash
# Ping Redis to make sure it is running
redis-cli PING
# Expected: PONG

# See all keys in Redis (careful in production!)
redis-cli KEYS '*'

# Check how much memory Redis is using
redis-cli INFO memory

# Flush everything (NUCLEAR OPTION -- development only!)
redis-cli FLUSHALL
```

---

## 8. Code Walkthrough of tasks.py

Let's go through `tasks.py` section by section. This is the actual file in the
Pulse project.

### Imports

```python
from utils.twilio_client import send_sms
from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

load_dotenv()
```

- `send_sms` is the function from `utils/twilio_client.py` that actually calls
  the Twilio API. The Celery tasks delegate to this function.
- `Celery` is the main class from the Celery library.
- `crontab` lets us define periodic schedules (like Unix cron).
- `load_dotenv()` reads the `.env` file so `os.getenv()` can find `REDIS_URL`.

### Celery instance configuration

```python
celery = Celery('tasks', broker=os.getenv('REDIS_URL'), backend=os.getenv('REDIS_URL'))
```

This creates the Celery application instance. Let's break down the arguments:

- `'tasks'` -- The name of the Celery app. By convention, this matches the
  module name (`tasks.py`). Celery uses this to discover tasks.
- `broker=os.getenv('REDIS_URL')` -- Where to send task messages. This is your
  Redis URL (e.g., `redis://localhost:6379/0`).
- `backend=os.getenv('REDIS_URL')` -- Where to store task results. Also Redis.

Both the broker and backend use the same Redis instance, which is perfectly fine
for a project of this size.

### Beat schedule configuration

```python
celery.conf.beat_schedule = {
    'check-reminders-daily': {
        'task': 'tasks.check_and_send_reminders',
        'schedule': crontab(minute=0, hour=8),
    },
}
celery.conf.timezone = 'UTC'
```

This tells Celery Beat: "Every day at 8:00 AM UTC, push a
`tasks.check_and_send_reminders` message onto the queue."

The `'check-reminders-daily'` key is just a human-readable name. You could call
it anything. The `'task'` value must be the full dotted path to the task
function.

Setting `timezone = 'UTC'` ensures the schedule runs based on UTC, not your
local machine time. This avoids confusion when deploying to servers in different
time zones.

### Task 1: send_reminder

```python
@celery.task
def send_reminder(to, message):
    return send_sms(to, message)
```

This is the simpler of the two tasks. It takes a phone number and a message,
then calls `send_sms()` to deliver it via Twilio.

**How it gets called** (from `routes/reminders.py`):

```python
# In send_reminder_now() route handler:
from tasks import send_reminder
send_reminder.delay(worker.phone, reminder.message)
```

The `.delay()` call serializes `worker.phone` and `reminder.message` as JSON,
pushes it into the Redis queue, and returns immediately. The Flask route does
not wait for Twilio to respond.

**Return value:** `send_sms()` returns the Twilio message SID (a string like
`"SM1234abc..."`) on success, or `None` on failure. This return value gets
stored in Redis as the task result.

### Task 2: check_and_send_reminders

```python
@celery.task
def check_and_send_reminders():
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
```

This is the more complex task. Let's walk through it piece by piece.

#### Why are imports inside the function?

```python
from app import app
from models.reminder import Reminder
...
```

These imports are **inside** the function, not at the top of the file. This is
intentional and important. It avoids **circular imports**:

- `tasks.py` imports from `utils/twilio_client.py` at the top level (fine).
- But `check_and_send_reminders` needs `app` from `app.py`.
- And `app.py` might indirectly import from `tasks.py` (through routes).
- If both files imported each other at the top level, Python would crash with a
  circular import error.

By importing inside the function, the import only happens when the function is
actually called, by which time both modules are fully loaded.

#### Why app.app_context()?

```python
with app.app_context():
    ...
```

Celery workers run in a **separate process** from Flask. They do not
automatically have access to Flask's application context, which SQLAlchemy needs
to connect to the database.

`app.app_context()` creates a temporary Flask application context so that
`Reminder.query`, `db.session`, and other Flask-SQLAlchemy features work
correctly inside the Celery worker.

Without this line, you would get an error like:
```
RuntimeError: Working outside of application context.
```

#### The query

```python
due_reminders = Reminder.query.filter(
    Reminder.scheduled_date <= date.today(),
    Reminder.status == 'pending'
).all()
```

This finds all reminders where:
- The `scheduled_date` is today or earlier (including overdue ones).
- The `status` is still `'pending'` (not already sent or completed).

#### The loop

```python
for reminder in due_reminders:
    worker = reminder.assigned_worker    # SQLAlchemy relationship
    if worker and worker.phone:
        send_reminder.delay(worker.phone, reminder.message)   # async!
        reminder.status = 'sent'
        reminder.sent_at = datetime.now(timezone.utc)

        event = TaskEvent(
            reminder_id=reminder.id,
            worker_id=worker.id,
            event_type='sent'
        )
        db.session.add(event)
        sent_count += 1
```

For each due reminder:
1. Get the assigned worker (via the SQLAlchemy relationship on the Reminder model).
2. If the worker exists and has a phone number, queue a `send_reminder` task.
3. Mark the reminder as `'sent'` and record the timestamp.
4. Create a `TaskEvent` with `event_type='sent'` for the audit log.

Notice that `send_reminder.delay()` is called *inside another task*. This is
called **task chaining** or **task fan-out**. The `check_and_send_reminders`
task itself does not send any messages -- it just queues up individual
`send_reminder` tasks. This means each message delivery is independently
tracked, retryable, and loggable.

#### The commit and return

```python
db.session.commit()
return f'Processed {sent_count} of {len(due_reminders)} due reminders'
```

All database changes (status updates and new TaskEvent rows) are committed in a
single transaction. The return string is stored in Redis as the task result --
handy for debugging.

---

## Quick Reference Cheat Sheet

```
Start Redis:          redis-server
Start Worker:         celery -A tasks worker --loglevel=info
Start Beat:           celery -A tasks beat --loglevel=info
Start Flask:          python app.py

Check queue length:   redis-cli LLEN celery
Check active tasks:   celery -A tasks inspect active
Check registered:     celery -A tasks inspect registered
Clear the queue:      celery -A tasks purge
Watch Redis live:     redis-cli MONITOR
```

---

## Further Reading

- [Celery Documentation](https://docs.celeryq.dev/en/stable/)
- [Redis Documentation](https://redis.io/docs/)
- [Flask + Celery Guide](https://flask.palletsprojects.com/en/latest/patterns/celery/)
- [Celery Best Practices](https://docs.celeryq.dev/en/stable/userguide/tasks.html#best-practices)
- [Twilio Python SDK](https://www.twilio.com/docs/libraries/python)
