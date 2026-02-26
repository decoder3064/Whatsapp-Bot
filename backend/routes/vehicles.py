from flask import Blueprint, request, jsonify
from models.vehicle import Vehicle
from models import db

vehicles_bp = Blueprint('vehicles', __name__, url_prefix='/api/vehicles')


@vehicles_bp.route('', methods=['POST'])
def add_vehicle():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400
    try:
        vehicle = Vehicle(
            driver_id=data['driver_id'],
            make=data['make'],
            model=data['model'],
            plate=data['plate'],
            year=data['year']
        )
        db.session.add(vehicle)
        db.session.commit()
        return jsonify({'message': 'Vehicle added successfully', 'id': vehicle.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@vehicles_bp.route('', methods=['GET'])
def get_vehicles():
    vehicles = Vehicle.query.all()
    result = [
        {
            'id': v.id,
            'driver': {
                'id': v.driver.id,
                'name': v.driver.name,
            } if v.driver else None,
            'make': v.make,
            'model': v.model,
            'plate': v.plate,
            'year': v.year
        }
        for v in vehicles
    ]
    return jsonify(result), 200


@vehicles_bp.route('/<int:vehicle_id>', methods=['GET'])
def get_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    return jsonify({
        'id': vehicle.id,
        'driver': {
            'id': vehicle.driver.id,
            'name': vehicle.driver.name,
        } if vehicle.driver else None,
        'make': vehicle.make,
        'model': vehicle.model,
        'plate': vehicle.plate,
        'year': vehicle.year
    }), 200


@vehicles_bp.route('/<int:vehicle_id>', methods=['PUT'])
def update_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    data = request.get_json()
    try:
        if 'driver_id' in data:
            vehicle.driver_id = data['driver_id']
        if 'make' in data:
            vehicle.make = data['make']
        if 'model' in data:
            vehicle.model = data['model']
        if 'plate' in data:
            vehicle.plate = data['plate']
        if 'year' in data:
            vehicle.year = data['year']
        db.session.commit()
        return jsonify({'message': 'Vehicle updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@vehicles_bp.route('/<int:vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    db.session.delete(vehicle)
    db.session.commit()
    return jsonify({'message': 'Vehicle deleted successfully'}), 200
