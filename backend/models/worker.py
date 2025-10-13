from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()



class Worker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(50), nullable=True)  
    givingServiceTo = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, default=True) 

    def __repr__(self):
        return f'<Worker {self.name} - {self.role}>'