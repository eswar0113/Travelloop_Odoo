from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import uuid

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    photo_url = db.Column(db.String(500))
    language = db.Column(db.String(10), default='en')
    phone = db.Column(db.String(20))
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    trips = db.relationship('Trip', backref='user', lazy=True, cascade='all, delete-orphan')
    posts = db.relationship('CommunityPost', backref='author', lazy=True, cascade='all, delete-orphan')


class Trip(db.Model):
    __tablename__ = 'trips'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    cover_photo = db.Column(db.String(500))
    is_public = db.Column(db.Boolean, default=False)
    share_token = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    budget_target = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    stops = db.relationship('Stop', backref='trip', lazy=True,
                            cascade='all, delete-orphan', order_by='Stop.order_index')
    budget_items = db.relationship('BudgetItem', backref='trip', lazy=True, cascade='all, delete-orphan')
    packing_items = db.relationship('PackingItem', backref='trip', lazy=True, cascade='all, delete-orphan')
    notes = db.relationship('TripNote', backref='trip', lazy=True, cascade='all, delete-orphan')

    @property
    def total_days(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0

    @property
    def total_budget(self):
        activity_cost = sum(
            (sa.custom_cost if sa.custom_cost is not None else sa.activity.estimated_cost)
            for stop in self.stops
            for sa in stop.stop_activities
        )
        manual_cost = sum(item.amount for item in self.budget_items)
        return round(activity_cost + manual_cost, 2)


class City(db.Model):
    __tablename__ = 'cities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(100))
    cost_index = db.Column(db.Float, default=50.0)
    popularity = db.Column(db.Integer, default=50)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    activities = db.relationship('Activity', backref='city', lazy=True)


class Stop(db.Model):
    __tablename__ = 'stops'
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    arrival_date = db.Column(db.Date)
    departure_date = db.Column(db.Date)
    order_index = db.Column(db.Integer, default=0)
    city = db.relationship('City')
    stop_activities = db.relationship('StopActivity', backref='stop', lazy=True,
                                      cascade='all, delete-orphan')

    @property
    def days(self):
        if self.arrival_date and self.departure_date:
            return (self.departure_date - self.arrival_date).days + 1
        return 0

    @property
    def activity_cost(self):
        return sum(
            (sa.custom_cost if sa.custom_cost is not None else sa.activity.estimated_cost)
            for sa in self.stop_activities
        )


class Activity(db.Model):
    __tablename__ = 'activities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    category = db.Column(db.String(50))
    estimated_cost = db.Column(db.Float, default=0.0)
    duration_hours = db.Column(db.Float, default=2.0)
    image_url = db.Column(db.String(500))


class StopActivity(db.Model):
    __tablename__ = 'stop_activities'
    id = db.Column(db.Integer, primary_key=True)
    stop_id = db.Column(db.Integer, db.ForeignKey('stops.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)
    scheduled_date = db.Column(db.Date)
    custom_cost = db.Column(db.Float)
    activity = db.relationship('Activity')


class BudgetItem(db.Model):
    __tablename__ = 'budget_items'
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    category = db.Column(db.String(50))
    label = db.Column(db.String(200))
    amount = db.Column(db.Float, default=0.0)


class PackingItem(db.Model):
    __tablename__ = 'packing_items'
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), default='other')
    is_packed = db.Column(db.Boolean, default=False)


class TripNote(db.Model):
    __tablename__ = 'trip_notes'
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    stop_id = db.Column(db.Integer, db.ForeignKey('stops.id'), nullable=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    linked_stop = db.relationship('Stop')


class CommunityPost(db.Model):
    __tablename__ = 'community_posts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=True)
    image_url = db.Column(db.String(500))
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    city = db.relationship('City')
    trip = db.relationship('Trip')
