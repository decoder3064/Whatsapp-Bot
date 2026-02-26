from flask import Blueprint, request, jsonify
from models import db
from models.worker import Worker

workers_bp = Blueprint('workers', __name__, url_prefix='/api/workers')


def serialize_worker(w, include_details=False):
    data = {
        'id': w.id,
        'name': w.name,
        'phone': w.phone,
        'email': w.email,
        'role': w.role,
        'givingServiceTo': w.givingServiceTo,
        'is_active': w.is_active,
    }
    if include_details:
        data['vehicles'] = [
            {
                'id': v.id,
                'make': v.make,
                'model': v.model,
                'plate': v.plate,
                'year': v.year,
            }
            for v in w.owned_vehicles
        ]
        data['reminders'] = [
            {
                'id': r.id,
                'reminder_type': r.reminder_type,
                'scheduled_date': r.scheduled_date.isoformat(),
                'message': r.message,
                'status': r.status,
                'sent_at': r.sent_at.isoformat() if r.sent_at else None,
                'completed_at': r.completed_at.isoformat() if r.completed_at else None,
                'created_at': r.created_at.isoformat(),
            }
            for r in w.assigned_tasks
        ]
    return data


@workers_bp.route('', methods=['POST'])
def add_worker():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    required_fields = ['name', 'phone', 'email']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    try:
        worker = Worker(
            name=data['name'],
            phone=data['phone'],
            email=data['email'],
            role=data.get('role'),
            givingServiceTo=data.get('givingServiceTo'),
            is_active=data.get('is_active', True)
        )
        db.session.add(worker)
        db.session.commit()
        return jsonify({
            'message': 'Worker added successfully',
            'worker': serialize_worker(worker)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@workers_bp.route('', methods=['GET'])
def get_workers():
    query = Worker.query

    is_active = request.args.get('is_active')
    if is_active is not None:
        query = query.filter(Worker.is_active == (is_active.lower() == 'true'))

    role = request.args.get('role')
    if role:
        query = query.filter(Worker.role == role)

    workers = query.all()
    return jsonify([serialize_worker(w) for w in workers]), 200


@workers_bp.route('/<int:worker_id>', methods=['GET'])
def get_worker(worker_id):
    worker = Worker.query.get_or_404(worker_id)
    return jsonify(serialize_worker(worker, include_details=True)), 200


@workers_bp.route('/<int:worker_id>', methods=['PUT'])
def update_worker(worker_id):
    worker = Worker.query.get_or_404(worker_id)
    data = request.get_json()

    try:
        if 'name' in data:
            worker.name = data['name']
        if 'phone' in data:
            worker.phone = data['phone']
        if 'email' in data:
            worker.email = data['email']
        if 'role' in data:
            worker.role = data['role']
        if 'givingServiceTo' in data:
            worker.givingServiceTo = data['givingServiceTo']
        if 'is_active' in data:
            worker.is_active = data['is_active']

        db.session.commit()
        return jsonify({
            'message': 'Worker updated successfully',
            'worker': serialize_worker(worker)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@workers_bp.route('/<int:worker_id>', methods=['DELETE'])
def delete_worker(worker_id):
    worker = Worker.query.get_or_404(worker_id)
    worker.is_active = False
    db.session.commit()
    return jsonify({'message': 'Worker deactivated successfully'}), 200
