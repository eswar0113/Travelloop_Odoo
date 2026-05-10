from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, User, Trip, Stop, City, Activity, StopActivity
from sqlalchemy import func
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)

ADMIN_EMAIL = 'admin@traveloop.com'


def _admin_guard():
    if current_user.email != ADMIN_EMAIL:
        flash('Access denied.', 'error')
        return redirect(url_for('trips.dashboard'))


@admin_bp.route('/admin')
@login_required
def dashboard():
    if current_user.email != ADMIN_EMAIL:
        flash('Access denied.', 'error')
        return redirect(url_for('trips.dashboard'))

    total_users      = User.query.count()
    total_trips      = Trip.query.count()
    total_stops      = Stop.query.count()
    public_trips     = Trip.query.filter_by(is_public=True).count()
    total_activities = StopActivity.query.count()

    top_cities = db.session.query(City.name, func.count(Stop.id).label('cnt'))\
                           .join(Stop, Stop.city_id == City.id)\
                           .group_by(City.id)\
                           .order_by(func.count(Stop.id).desc()).limit(10).all()

    top_activities = db.session.query(Activity.name, Activity.category,
                                      func.count(StopActivity.id).label('cnt'))\
                               .join(StopActivity, StopActivity.activity_id == Activity.id)\
                               .group_by(Activity.id)\
                               .order_by(func.count(StopActivity.id).desc()).limit(8).all()

    recent_users  = User.query.order_by(User.created_at.desc()).limit(10).all()
    recent_trips  = Trip.query.order_by(Trip.created_at.desc()).limit(10).all()

    trips_per_user = db.session.query(
        User.name, func.count(Trip.id).label('cnt')
    ).join(Trip, Trip.user_id == User.id, isouter=True)\
     .group_by(User.id).order_by(func.count(Trip.id).desc()).limit(10).all()

    # Signups per day — last 30 days (Python-side bucketing for portability)
    cutoff = datetime.utcnow() - timedelta(days=29)
    new_users = User.query.filter(User.created_at >= cutoff).all()
    day_buckets = {}
    for i in range(30):
        d = (cutoff + timedelta(days=i)).strftime('%b %d')
        day_buckets[d] = 0
    for u in new_users:
        key = u.created_at.strftime('%b %d')
        if key in day_buckets:
            day_buckets[key] += 1
    signup_labels = list(day_buckets.keys())
    signup_data   = list(day_buckets.values())

    return render_template('admin.html',
                           total_users=total_users, total_trips=total_trips,
                           total_stops=total_stops, public_trips=public_trips,
                           total_activities=total_activities,
                           top_cities=top_cities, top_activities=top_activities,
                           recent_users=recent_users, recent_trips=recent_trips,
                           trips_per_user=trips_per_user,
                           signup_labels=signup_labels, signup_data=signup_data)


@admin_bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.email != ADMIN_EMAIL:
        flash('Access denied.', 'error')
        return redirect(url_for('trips.dashboard'))
    user = User.query.get_or_404(user_id)
    if user.email == ADMIN_EMAIL:
        flash('Cannot delete the admin account.', 'error')
        return redirect(url_for('admin.dashboard'))
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.name} deleted.', 'success')
    return redirect(url_for('admin.dashboard'))
