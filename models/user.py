from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

   


class Rehber(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    ad = db.Column(db.String(50), unique=True, nullable=False)
    soyad = db.Column(db.String(50), unique=True, nullable=False)
    numara = db.Column(db.String(50), unique=True, nullable=False)

   

    
    

    