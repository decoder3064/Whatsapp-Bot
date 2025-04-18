from flask import Blueprint, request, jsonify
from models.vehicle import Vehicle, db
from utils.twilio_client import send_sms



vehicles_bp = Blueprint('vehicles', __name__)

@vehicles_bp.route('/add_vehicle', methods=['POST'])
def add_vehicle():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400
    try:
        vehicle = Vehicle(
            driver=data['driver'],
            phone=data['phone'],
            make=data['make'],
            model=data['model'],
            plate=data['plate'],
            year=data['year']
        )
        db.session.add(vehicle)
        db.session.commit()
        return jsonify({'message': 'Vehicle added successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    


@vehicles_bp.route('/get_vehicles', methods=['GET'])    
def get_vehicles():
    vehicles = Vehicle.query.all()
    result = [
        {
            'id': v.id,
            'driver': v.driver,
            'phone': v.phone,
            'make': v.make,
            'model': v.model,
            'plate': v.plate,
            'year': v.year
        } 
        for v in vehicles
    ]
    return jsonify(result)


@vehicles_bp.route('/test_whatsapp', methods=['POST'])
def test_whatsapp():
    data = request.get_json()
    phone = data.get('phone')
    message = data.get('message')

    if not phone or not message:
        return jsonify({'error': 'Phone number and message are required'}), 400
    
    send_sms(phone, message)
    return jsonify({'message': 'WhatsApp message sent successfully'}), 200


   









