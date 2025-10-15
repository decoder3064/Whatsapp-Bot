from flask import Blueprint, request, jsonify
from models.vehicle import Vehicle, db
from utils.twilio_client import send_sms



vehicles_bp = Blueprint('vehicles', __name__)


#POST ROUTE
@vehicles_bp.route('/add_vehicle', methods=['POST'])
def add_vehicle():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400
    try:
        vehicle = Vehicle(
            driver_id=data['driver_id'],
            phone=data['phone'],
            make=data['make'],
            model=data['model'],
            plate=data['plate'],
            year=data['year']
        )
        db.session.add(vehicle)
        db.session.commit()
        return jsonify({'message': 'Vehicle added successfully',
                        'id': vehicle.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    

# GET ROUTES 
@vehicles_bp.route('/get_vehicles', methods=['GET'])    
def get_vehicles():
    vehicles = Vehicle.query.all()
    result = [
        {
            'id': v.id,
            'driver':{
                'id':v.driver.id,
                'name': v.driver.name,
                'phone': v.driver.phone,
            },
            'make': v.make,
            'model': v.model,
            'plate': v.plate,
            'year': v.year
        } 
        for v in vehicles]
    return jsonify(result), 200

@vehicles_bp.route('/<int:vehicle_id>', methods=['GET'])
def get_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    return jsonify(
        {
            'id': vehicle.id,
            'driver':{
                'id':vehicle.driver.id,
                'name': vehicle.driver.name,
                'phone': vehicle.driver.phone,
            },
            'make': vehicle.make,
            'model': vehicle.model,
            'plate': vehicle.plate,
            'year': vehicle.year
        }),200

#UPDATE ROUTE
@vehicles_bp.route('/<int:vehicle_id>', methods=['PUT'])
def update_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    data = request.get_json()


    if 'dirver_id' in data:
        vehicle.driver_id = data['driver_id']
    if 'make' in data: 
        vehicle.make = data['make']
    if 'model' in data:
        vehicle.driver_id = data['model']
    if 'plate' in data: 
        vehicle.make = data['plate']
    if 'year' in data:
        vehicle.driver_id = data['year']
    
    db.session.commit()
    return jsonify({'message': 'Vehicle updated successfully'}), 200


#DELETE ROUTE
@vehicles_bp.route('/<int:vehicle_id>', methods=['DELET'])
def delete_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    db.session.delete(vehicle)
    db.session.commit()
    return jsonify({'message':'Vehicle deleted successfully'}),200
  
    




   









