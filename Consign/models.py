
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Offer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(100), nullable=False)
    size = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    partner_id = db.Column(db.Integer, db.ForeignKey('partner.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Dostupné")

    partner = db.relationship('Partner', back_populates='offers')

class Partner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    offers = db.relationship('Offer', back_populates='partner')
