from models import db 

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('worker.id'), nullable=False)
    driver = db.relationship('Worker', foreign_keys=[driver_id], backref='owned_vehicles')
    make = db.Column(db.String(80), nullable=False)
    model = db.Column(db.String(80), nullable=False)
    plate = db.Column(db.String(80), nullable=False)
    year = db.Column(db.Integer, nullable=False)



    def __repr__(self):
        return f'<Vehicle {self.make} {self.model} {self.year}>'
    

    