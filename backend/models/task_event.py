from models import db
from datetime import datetime, timezone


class TaskEvent(db.Model):
    """
    Tracks lifecycle events for reminders/tasks. Each row is an immutable
    event record. This is an append-only log — rows are never updated.

    event_type values:
        'created'      - reminder was created
        'sent'         - reminder was sent via WhatsApp
        'completed'    - task was marked as completed
        'overdue'      - reminder passed its date without being sent/completed
    """
    id = db.Column(db.Integer, primary_key=True)
    reminder_id = db.Column(db.Integer, db.ForeignKey('reminder.id'), nullable=False)
    reminder = db.relationship('Reminder', backref='events')
    worker_id = db.Column(db.Integer, db.ForeignKey('worker.id'), nullable=False)
    event_type = db.Column(db.String(30), nullable=False)
    occurred_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<TaskEvent {self.event_type} - Reminder {self.reminder_id}>'
