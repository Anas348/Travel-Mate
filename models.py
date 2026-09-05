"""
Database models for TravelMate.

These are plain SQLAlchemy models, not tied to any specific database engine.
Point DATABASE_URL (see config.py) at SQLite, PostgreSQL, or MySQL and the
same models create the same schema everywhere -- see README.md, section
"Working with the database".
"""
from datetime import date

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="traveler")  # traveler | admin

    hotels = db.relationship("Hotel", backref="owner", lazy=True)
    reviews = db.relationship("Review", backref="author", lazy=True)
    favourites = db.relationship("Favourite", backref="user", lazy=True)
    destinations = db.relationship("Destination", backref="added_by_user", lazy=True)

    @property
    def is_admin(self):
        return self.role == "admin"


class Hotel(db.Model):
    __tablename__ = "hotels"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    price_per_night = db.Column(db.Numeric(10, 2), nullable=False)
    rating = db.Column(db.Numeric(2, 1), default=0)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))

    rooms = db.relationship("Room", backref="hotel", cascade="all, delete-orphan", lazy=True)
    reviews = db.relationship("Review", backref="hotel", cascade="all, delete-orphan", lazy=True)
    favourited_by = db.relationship("Favourite", backref="hotel", cascade="all, delete-orphan", lazy=True)
    amenities = db.relationship("Amenity", secondary="hotel_amenity", backref="hotels", lazy=True)

    @property
    def average_rating(self):
        if not self.reviews:
            return self.rating or 0
        return round(sum(r.rating for r in self.reviews) / len(self.reviews), 1)


class Room(db.Model):
    __tablename__ = "rooms"

    id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False)
    room_type = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    availability_status = db.Column(db.Boolean, default=True)


class Favourite(db.Model):
    __tablename__ = "favourites"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (db.UniqueConstraint("user_id", "hotel_id", name="uq_user_hotel_fav"),)


class Destination(db.Model):
    __tablename__ = "destinations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    travel_tips = db.Column(db.Text)
    added_by = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))

    attractions = db.relationship("Attraction", backref="destination", cascade="all, delete-orphan", lazy=True)


class Attraction(db.Model):
    __tablename__ = "attractions"

    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(db.Integer, db.ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(255))


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    review_date = db.Column(db.Date, default=date.today)


class Amenity(db.Model):
    __tablename__ = "amenities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)


class HotelAmenity(db.Model):
    __tablename__ = "hotel_amenity"

    hotel_id = db.Column(db.Integer, db.ForeignKey("hotels.id", ondelete="CASCADE"), primary_key=True)
    amenity_id = db.Column(db.Integer, db.ForeignKey("amenities.id", ondelete="CASCADE"), primary_key=True)
