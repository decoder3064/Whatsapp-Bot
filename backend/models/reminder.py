from models import db 
from datetime import datetime,timezone

class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    assigned_worker_id = db.Column(db.Integer, db.ForeignKey('worker.id'), nullable=False)
    assigned_worker = db.relationship('Worker', backref='assigned_tasks')  
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=True)
    vehicle = db.relationship('Vehicle', backref='service_reminders')  
    reminder_type = db.Column(db.String(50), nullable=False) 
    scheduled_date = db.Column(db.Date, nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending') 
    sent_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

   
    def __repr__(self):
        vehicle_info = f" for Vehicle {self.vehicle_id}" if self.vehicle_id else ""
        return f'<Reminder {self.reminder_type}{vehicle_info} - Worker {self.assigned_worker_id}>'