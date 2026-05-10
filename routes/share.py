from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Trip, Stop, StopActivity

share_bp = Blueprint('share', __name__)


@share_bp.route('/share/<token>')
def public_view(token):
    trip = Trip.query.filter_by(share_token=token, is_public=True).first_or_404()
    total_activities = sum(len(s.stop_activities) for s in trip.stops)
    return render_template('share.html', trip=trip, total_activities=total_activities)


@share_bp.route('/share/<token>/copy', methods=['POST'])
@login_required
def copy_trip(token):
    original = Trip.query.filter_by(share_token=token, is_public=True).first_or_404()

    new_trip = Trip(
        user_id=current_user.id,
        name=f'Copy of {original.name}',
        description=original.description,
        start_date=original.start_date,
        end_date=original.end_date,
        cover_photo=original.cover_photo,
    )
    db.session.add(new_trip)
    db.session.flush()

    for stop in original.stops:
        new_stop = Stop(
            trip_id=new_trip.id,
            city_id=stop.city_id,
            arrival_date=stop.arrival_date,
            departure_date=stop.departure_date,
            order_index=stop.order_index,
        )
        db.session.add(new_stop)
        db.session.flush()
        for sa in stop.stop_activities:
            db.session.add(StopActivity(
                stop_id=new_stop.id,
                activity_id=sa.activity_id,
                custom_cost=sa.custom_cost,
            ))

    db.session.commit()
    flash(f'"{original.name}" copied to your trips!', 'success')
    return redirect(url_for('trips.builder', trip_id=new_trip.id))


@share_bp.route('/trips/<int:trip_id>/toggle-public', methods=['POST'])
@login_required
def toggle_public(trip_id):
    trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first_or_404()
    trip.is_public = not trip.is_public
    db.session.commit()
    status = 'public' if trip.is_public else 'private'
    flash(f'Trip is now {status}.', 'success')
    return redirect(url_for('trips.view_trip', trip_id=trip_id))
