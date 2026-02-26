from flask import Blueprint, request, jsonify
from models import db
from models.reminder import Reminder
from models.worker import Worker
from models.vehicle import Vehicle
from models.task_event import TaskEvent
from datetime import datetime, date, timezone

reminders_bp = Blueprint('reminders', __name__, url_prefix='/api/reminders')


def serialize_reminder(r):
    return {
        'id': r.id,
        'assigned_worker': {
            'id': r.assigned_worker.id,
            'name': r.assigned_worker.name,
        } if r.assigned_worker else None,
        'vehicle': {
            'id': r.vehicle.id,
            'plate': r.vehicle.plate,
            'make': r.vehicle.make,
            'model': r.vehicle.model,
        } if r.vehicle else None,
        'reminder_type': r.reminder_type,
        'scheduled_date': r.scheduled_date.isoformat(),
        'message': r.message,
        'status': r.status,
        'sent_at': r.sent_at.isoformat() if r.sent_at else None,
        'completed_at': r.completed_at.isoformat() if r.completed_at else None,
        'created_at': r.created_at.isoformat(),
    }


@reminders_bp.route('', methods=['POST'])
def add_reminder():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    required_fields = ['assigned_worker_id', 'reminder_type', 'scheduled_date', 'message']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    try:
        scheduled_date = datetime.strptime(data['scheduled_date'], '%Y-%m-%d').date()

        reminder = Reminder(
            assigned_worker_id=data['assigned_worker_id'],
            vehicle_id=data.get('vehicle_id'),
            reminder_type=data['reminder_type'],
            scheduled_date=scheduled_date,
            message=data['message'],
            status=data.get('status', 'pending')
        )
        db.session.add(reminder)
        db.session.flush()

        event = TaskEvent(
            reminder_id=reminder.id,
            worker_id=reminder.assigned_worker_id,
            event_type='created'
        )
        db.session.add(event)
        db.session.commit()

        return jsonify({
            'message': 'Reminder added successfully',
            'reminder': serialize_reminder(reminder)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@reminders_bp.route('', methods=['GET'])
def get_reminders():
    query = Reminder.query

    status = request.args.get('status')
    if status:
        query = query.filter(Reminder.status == status)

    worker_id = request.args.get('worker_id')
    if worker_id:
        query = query.filter(Reminder.assigned_worker_id == int(worker_id))

    from_date = request.args.get('from_date')
    if from_date:
        query = query.filter(Reminder.scheduled_date >= datetime.strptime(from_date, '%Y-%m-%d').date())

    to_date = request.args.get('to_date')
    if to_date:
        query = query.filter(Reminder.scheduled_date <= datetime.strptime(to_date, '%Y-%m-%d').date())

    reminders = query.order_by(Reminder.scheduled_date.desc()).all()
    return jsonify([serialize_reminder(r) for r in reminders]), 200


@reminders_bp.route('/<int:reminder_id>', methods=['GET'])
def get_reminder(reminder_id):
    reminder = Reminder.query.get_or_404(reminder_id)
    return jsonify(serialize_reminder(reminder)), 200


@reminders_bp.route('/<int:reminder_id>', methods=['PUT'])
def update_reminder(reminder_id):
    reminder = Reminder.query.get_or_404(reminder_id)
    data = request.get_json()

    try:
        if 'assigned_worker_id' in data:
            reminder.assigned_worker_id = data['assigned_worker_id']
        if 'vehicle_id' in data:
            reminder.vehicle_id = data['vehicle_id']
        if 'reminder_type' in data:
            reminder.reminder_type = data['reminder_type']
        if 'scheduled_date' in data:
            reminder.scheduled_date = datetime.strptime(data['scheduled_date'], '%Y-%m-%d').date()
        if 'message' in data:
            reminder.message = data['message']
        if 'status' in data:
            old_status = reminder.status
            reminder.status = data['status']
            if data['status'] == 'completed' and old_status != 'completed':
                reminder.completed_at = datetime.now(timezone.utc)
                event = TaskEvent(
                    reminder_id=reminder.id,
                    worker_id=reminder.assigned_worker_id,
                    event_type='completed'
                )
                db.session.add(event)

        db.session.commit()
        return jsonify({
            'message': 'Reminder updated successfully',
            'reminder': serialize_reminder(reminder)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@reminders_bp.route('/<int:reminder_id>', methods=['DELETE'])
def delete_reminder(reminder_id):
    reminder = Reminder.query.get_or_404(reminder_id)
    db.session.delete(reminder)
    db.session.commit()
    return jsonify({'message': 'Reminder deleted successfully'}), 200


@reminders_bp.route('/<int:reminder_id>/send', methods=['POST'])
def send_reminder_now(reminder_id):
    reminder = Reminder.query.get_or_404(reminder_id)
    worker = reminder.assigned_worker

    if not worker or not worker.phone:
        return jsonify({'error': 'Worker has no phone number'}), 400

    try:
        from tasks import send_reminder
        send_reminder.delay(worker.phone, reminder.message)

        reminder.status = 'sent'
        reminder.sent_at = datetime.now(timezone.utc)

        event = TaskEvent(
            reminder_id=reminder.id,
            worker_id=worker.id,
            event_type='sent'
        )
        db.session.add(event)
        db.session.commit()

        return jsonify({'message': 'Reminder sent successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
