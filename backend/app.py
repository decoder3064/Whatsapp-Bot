from flask import Flask
from flask_cors import CORS
from models import db
from routes.vehicles import vehicles_bp
from routes.reminders import reminders_bp
from routes.workers import workers_bp
from routes.auth import auth_bp
from routes.metrics import metrics_bp
from routes.chat import chat_bp
from flask.cli import with_appcontext
import os
import click
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# CORS — allow the React dev server and frontend
CORS(app, 
     resources={r"/api/*": {"origins": "*"}},
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://localhost/whatsapp_bot')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'change-this-in-production')

# Initialize database
db.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(vehicles_bp)
app.register_blueprint(reminders_bp)
app.register_blueprint(workers_bp)
app.register_blueprint(metrics_bp)
app.register_blueprint(chat_bp)


@app.route('/')
def home():
    return 'Pulse API is running'


# CLI commands
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Create database tables."""
    db.create_all()
    click.echo('Initialized the database.')


@click.command('add-mock-data')
@with_appcontext
def add_mock_data_command():
    """Add mock data to the database."""
    from models.worker import Worker
    from models.vehicle import Vehicle
    from models.reminder import Reminder
    from datetime import date

    worker = Worker(name='David Reyes', phone='+15551234567', email='david@example.com', role='driver', is_active=True)
    db.session.add(worker)
    db.session.flush()

    vehicle = Vehicle(driver_id=worker.id, make='Toyota', model='Camry', plate='EON123', year=2011)
    db.session.add(vehicle)
    db.session.flush()

    reminder = Reminder(
        assigned_worker_id=worker.id,
        vehicle_id=vehicle.id,
        reminder_type='oil_change',
        scheduled_date=date.today(),
        message='Reminder: Your Toyota Camry is due for an oil change.',
        status='pending'
    )
    db.session.add(reminder)
    db.session.commit()
    click.echo('Added mock data: 1 worker, 1 vehicle, 1 reminder.')


app.cli.add_command(init_db_command)
app.cli.add_command(add_mock_data_command)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
