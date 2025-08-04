#define the tables

import datetime
import enum
from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String
from application.database import db 

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    address = db.Column(db.String, unique=False, nullable=False)
    pincode = db.Column(db.Integer, unique=False, nullable=False)
    role = db.Column(db.String(80), unique=False, nullable=False)
    reservations = db.relationship("Reservation", back_populates="user")

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "username" : self.username,
            "email": self.email,
            "password" : self.password,
            "pincode": self.pincode,
            "role" : self.role
            # do not serialize the password, its a security breach
        }
    
class SpotStatus(enum.Enum):
    OCCUPIED = "O"
    AVAILABLE ="A"

class ParkingLot(db.Model):
    __tablename__ = "parking_lots"
    id = db.Column(Integer, primary_key=True)
    prime_location = db.Column(String, nullable=False)
    price = db.Column(Float, nullable=False)
    address = db.Column(String, nullable=False)
    pincode = db.Column(Integer, nullable=False)
    max_spot = db.Column(Integer, nullable=False)
    spots = db.relationship("ParkingSpot", back_populates="lot", cascade="all, delete-orphan")

class ParkingSpot(db.Model):
    __tablename__ = "parking_spots"
    id = db.Column(Integer, primary_key=True)
    lot_id = db.Column(Integer, ForeignKey("parking_lots.id"), nullable=False)
    status = db.Column(Enum(SpotStatus), default=SpotStatus.AVAILABLE, nullable=False)
    lot = db.relationship("ParkingLot", back_populates="spots")
    reservations = db.relationship("Reservation", back_populates="spot", cascade="all, delete-orphan")

class Reservation(db.Model):
    __tablename__ = "reservations"
    id = db.Column(Integer, primary_key=True)
    spot_id = db.Column(Integer, ForeignKey("parking_spots.id"), nullable=False)
    user_id = db.Column(Integer, ForeignKey("users.id"), nullable=False)
    parking_timestamp = db.Column(DateTime, default=datetime.datetime.utcnow)
    leaving_timestamp = db.Column(DateTime, nullable=False)
    packing_cost = db.Column(Float, nullable=False)
    vehicle_number = db.Column(String, nullable=False)
    status = db.Column(db.String, default='active')
    spot = db.relationship("ParkingSpot", back_populates="reservations")
    user = db.relationship("User", back_populates="reservations")
