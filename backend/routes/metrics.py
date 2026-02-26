from flask import Blueprint, request, jsonify
from models import db
from models.worker import Worker
from models.vehicle import Vehicle
from models.reminder import Reminder
from models.task_event import TaskEvent
from sqlalchemy import func, case
from datetime import datetime, date, timedelta, timezone

metrics_bp = Blueprint('metrics', __name__, url_prefix='/api/metrics')


@metrics_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    today = date.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    active_workers = Worker.query.filter_by(is_active=True).count()
    total_vehicles = Vehicle.query.count()

    # Reminder counts by status
    status_counts = db.session.query(
        Reminder.status,
        func.count(Reminder.id)
    ).group_by(Reminder.status).all()

    status_map = {status: count for status, count in status_counts}

    # Sent counts by period
    sent_today = Reminder.query.filter(
        Reminder.status == 'sent',
        func.date(Reminder.sent_at) == today
    ).count()

    sent_this_week = Reminder.query.filter(
        Reminder.status == 'sent',
        func.date(Reminder.sent_at) >= week_ago
    ).count()

    sent_this_month = Reminder.query.filter(
        Reminder.status == 'sent',
        func.date(Reminder.sent_at) >= month_ago
    ).count()

    # Overdue count
    overdue = Reminder.query.filter(
        Reminder.status == 'pending',
        Reminder.scheduled_date < today
    ).count()

    return jsonify({
        'active_workers': active_workers,
        'total_vehicles': total_vehicles,
        'reminders': {
            'pending': status_map.get('pending', 0),
            'sent': status_map.get('sent', 0),
            'completed': status_map.get('completed', 0),
            'overdue': overdue,
            'total': sum(status_map.values()),
        },
        'sent_today': sent_today,
        'sent_this_week': sent_this_week,
        'sent_this_month': sent_this_month,
    }), 200


@metrics_bp.route('/workers', methods=['GET'])
def get_worker_metrics():
    from_date_str = request.args.get('from_date')
    to_date_str = request.args.get('to_date')

    from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date() if from_date_str else date.today() - timedelta(days=365)
    to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date() if to_date_str else date.today()

    stats = db.session.query(
        Worker.id,
        Worker.name,
        Worker.is_active,
        func.count(Reminder.id).label('total_assigned'),
        func.count(case((Reminder.status == 'completed', 1))).label('total_completed'),
        func.count(case((Reminder.status == 'sent', 1))).label('total_sent'),
        func.count(case((Reminder.status == 'pending', 1))).label('total_pending'),
    ).outerjoin(
        Reminder, Reminder.assigned_worker_id == Worker.id
    ).filter(
        db.or_(
            Reminder.created_at.is_(None),
            db.and_(
                func.date(Reminder.created_at) >= from_date,
                func.date(Reminder.created_at) <= to_date
            )
        )
    ).group_by(Worker.id, Worker.name, Worker.is_active).all()

    result = []
    for row in stats:
        total = row.total_assigned or 0
        completed = row.total_completed or 0
        completion_rate = round((completed / total * 100), 1) if total > 0 else 0.0

        result.append({
            'worker_id': row.id,
            'worker_name': row.name,
            'is_active': row.is_active,
            'total_assigned': total,
            'total_completed': completed,
            'total_sent': row.total_sent or 0,
            'total_pending': row.total_pending or 0,
            'completion_rate': completion_rate,
        })

    result.sort(key=lambda x: x['total_assigned'], reverse=True)
    return jsonify(result), 200


@metrics_bp.route('/workers/<int:worker_id>', methods=['GET'])
def get_single_worker_metrics(worker_id):
    worker = Worker.query.get_or_404(worker_id)

    total = Reminder.query.filter_by(assigned_worker_id=worker_id).count()
    completed = Reminder.query.filter_by(assigned_worker_id=worker_id, status='completed').count()
    sent = Reminder.query.filter_by(assigned_worker_id=worker_id, status='sent').count()
    pending = Reminder.query.filter_by(assigned_worker_id=worker_id, status='pending').count()
    overdue = Reminder.query.filter(
        Reminder.assigned_worker_id == worker_id,
        Reminder.status == 'pending',
        Reminder.scheduled_date < date.today()
    ).count()

    completion_rate = round((completed / total * 100), 1) if total > 0 else 0.0

    # Recent events
    recent_events = TaskEvent.query.filter_by(worker_id=worker_id).order_by(
        TaskEvent.occurred_at.desc()
    ).limit(20).all()

    return jsonify({
        'worker': {
            'id': worker.id,
            'name': worker.name,
            'is_active': worker.is_active,
        },
        'metrics': {
            'total_assigned': total,
            'total_completed': completed,
            'total_sent': sent,
            'total_pending': pending,
            'total_overdue': overdue,
            'completion_rate': completion_rate,
        },
        'recent_events': [
            {
                'id': e.id,
                'reminder_id': e.reminder_id,
                'event_type': e.event_type,
                'occurred_at': e.occurred_at.isoformat(),
                'notes': e.notes,
            }
            for e in recent_events
        ],
    }), 200


@metrics_bp.route('/reminders', methods=['GET'])
def get_reminder_analytics():
    group_by = request.args.get('group_by', 'day')
    from_date_str = request.args.get('from_date')
    to_date_str = request.args.get('to_date')

    from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date() if from_date_str else date.today() - timedelta(days=30)
    to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date() if to_date_str else date.today()

    # Generate date series
    data_points = []
    current = from_date
    while current <= to_date:
        if group_by == 'day':
            next_date = current + timedelta(days=1)
        elif group_by == 'week':
            next_date = current + timedelta(weeks=1)
        elif group_by == 'month':
            next_date = current + timedelta(days=30)
        else:
            next_date = current + timedelta(days=1)

        created = Reminder.query.filter(
            func.date(Reminder.created_at) >= current,
            func.date(Reminder.created_at) < next_date
        ).count()

        sent = Reminder.query.filter(
            func.date(Reminder.sent_at) >= current,
            func.date(Reminder.sent_at) < next_date
        ).count()

        completed = Reminder.query.filter(
            func.date(Reminder.completed_at) >= current,
            func.date(Reminder.completed_at) < next_date
        ).count()

        data_points.append({
            'date': current.isoformat(),
            'created': created,
            'sent': sent,
            'completed': completed,
        })

        current = next_date

    return jsonify(data_points), 200
