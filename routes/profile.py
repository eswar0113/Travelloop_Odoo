from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, User, Trip, Stop, City
import bcrypt

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_profile':
            name = request.form.get('name', '').strip()
            photo_url = request.form.get('photo_url', '').strip()
            language = request.form.get('language', 'en')
            if name:
                current_user.name = name
            current_user.photo_url = photo_url or None
            current_user.language = language
            current_user.phone = request.form.get('phone', '').strip() or None
            current_user.city = request.form.get('city', '').strip() or None
            current_user.country = request.form.get('country', '').strip() or None
            current_user.bio = request.form.get('bio', '').strip() or None
            db.session.commit()
            flash('Profile updated.', 'success')

        elif action == 'change_password':
            old_pw = request.form.get('old_password', '')
            new_pw = request.form.get('new_password', '')
            confirm = request.form.get('confirm_password', '')
            if not bcrypt.checkpw(old_pw.encode(), current_user.password_hash.encode()):
                flash('Current password is incorrect.', 'error')
            elif new_pw != confirm:
                flash('New passwords do not match.', 'error')
            elif len(new_pw) < 6:
                flash('Password must be at least 6 characters.', 'error')
            else:
                current_user.password_hash = bcrypt.hashpw(
                    new_pw.encode(), bcrypt.gensalt()).decode()
                db.session.commit()
                flash('Password changed.', 'success')

        elif action == 'delete_account':
            db.session.delete(current_user)
            db.session.commit()
            flash('Account deleted.', 'info')
            return redirect(url_for('auth.signup'))

        return redirect(url_for('profile.profile'))

    saved_cities = db.session.query(City)\
        .join(Stop, Stop.city_id == City.id)\
        .join(Trip, Trip.id == Stop.trip_id)\
        .filter(Trip.user_id == current_user.id)\
        .distinct().order_by(City.name).limit(20).all()

    total_days = sum(t.total_days for t in current_user.trips)
    total_activities = sum(
        len(s.stop_activities) for t in current_user.trips for s in t.stops
    )
    total_stops = sum(len(t.stops) for t in current_user.trips)
    public_trips = sum(1 for t in current_user.trips if t.is_public)

    return render_template('profile.html', user=current_user,
                           saved_cities=saved_cities,
                           total_days=total_days,
                           total_activities=total_activities,
                           total_stops=total_stops,
                           public_trips=public_trips)
