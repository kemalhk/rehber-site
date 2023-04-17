from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, relationship


db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    authenticated = db.Column(db.Boolean, default=False)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.id

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False


class Rehber(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ad = db.Column(db.String(50), nullable=False)
    soyad = db.Column(db.String(50), nullable=False)
    numara = db.Column(db.String(50), unique=True, nullable=False)
    adresses = db.relationship("Adres", backref="Rehber", lazy=True)


class Adres(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String(120), unique=True, nullable=False)
    adres_adi=db.Column(db.String(30),nullable=False)
    il=db.Column(db.String(20),nullable=False)
    ilce=db.Column(db.String(25),nullable=False)
    adres=db.Column(db.String(90),nullable=False)
    rehber_id = db.Column(db.Integer, db.ForeignKey("rehber.id"), nullable=False)