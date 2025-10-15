from flask import Blueprint, request, jsonify
from models import db
from models.reminder import Reminder
from models.worker import Worker
from models.vehicle import Vehicle
from datetime import datetime, date

reminders_bp = Blueprint('reminders', __name__)

@reminders_bp.route('/add_reminder', methods=['POST'])
def add_vehicle():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No input data provided'}), 400
    
    required_fields = ['assigned_worker_id', 'reminder_type', 'scheduled_date', 'message']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    try:

        scheduled_date = datetime.strptime(data['scheduled_date'], '%Y-%m-%d').date()

        reminder= Reminder(
            assigned_worker_id = data['assigned_worker_id'],
            vahicle_id = data.get('vehicle_id'),
            reminder_type = data['reminder_type'],
            scheduled_date = scheduled_date,
            message = data['message'],
            status = data.get('status', 'pending'))
        
        db.session.add(reminder)
        db.session.commit()
        return jsonify({
            'message': 'Reminder added successfully',
            'id': reminder.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    

@reminders_bp.route('/', methods=['GET'])
def get_reminders():
    reminders = Reminder.query.all()
    result = [{
        'id': r.id,

    }
    for r in reminders
    ]