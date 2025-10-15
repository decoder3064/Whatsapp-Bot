from flask import Flask
from models import db
from flask.cli import with_appcontext
import os
import click
from routes.vehicles import vehicles_bp
from dotenv import load_dotenv
from config import REDIS_URL

app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://localhost/whatsapp_bot')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)
#app.run(debug=True)

@app.route('/')
def home():
    return "Flask app is running and connected to the vehicle table"

app.register_blueprint(reminders_bp)
app.register_blueprint(workers_bp)
app.register_blueprint(vehicles_bp)









#CLIs

# Flask CLI command to initialize the database
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Create database tables."""
    db.create_all()
    click.echo('Initialized the database.')


# Flask CLI command to add mock data to the database
@click.command('add-mock-data')
@with_appcontext
def add_mock_data_command():
    """Add mock data to the database."""
    from models.vehicle import Vehicle
    vehicle = Vehicle(driver='David', phone='8593121167', make='Toyota', model='Lexus', plate='EON123', year=2011)
    db.session.add(vehicle)
    db.session.commit()
    click.echo('Added mock data to the database.')
''
# Register the CLI commands
app.cli.add_command(init_db_command)
app.cli.add_command(add_mock_data_command)


if __name__ == "__main__":
    app.run(debug=True)

