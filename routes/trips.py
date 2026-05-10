from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, Trip, Stop, City, Activity, StopActivity, PackingItem, TripNote
from datetime import datetime, date
from utils.email import send_trip_summary, send_trip_created

trips_bp = Blueprint('trips', __name__)


@trips_bp.route('/dashboard')
@login_required
def dashboard():
    recent_trips = Trip.query.filter_by(user_id=current_user.id)\
                             .order_by(Trip.created_at.desc()).limit(4).all()
    popular_cities = City.query.order_by(City.popularity.desc()).limit(8).all()
    total_trips = Trip.query.filter_by(user_id=current_user.id).count()
    total_cities = db.session.query(Stop.city_id).join(Trip)\
                             .filter(Trip.user_id == current_user.id)\
                             .distinct().count()
    upcoming = Trip.query.filter_by(user_id=current_user.id)\
                         .filter(Trip.start_date >= date.today())\
                         .order_by(Trip.start_date).first()
    return render_template('dashboard.html', recent_trips=recent_trips,
                           popular_cities=popular_cities, total_trips=total_trips,
                           total_cities=total_cities, upcoming=upcoming)


@trips_bp.route('/trips')
@login_required
def my_trips():
    today = date.today()
    q = request.args.get('q', '').strip()
    all_trips = Trip.query.filter_by(user_id=current_user.id)\
                          .order_by(Trip.start_date.asc().nullslast(), Trip.created_at.desc()).all()

    if q:
        all_trips = [t for t in all_trips if q.lower() in t.name.lower()]

    ongoing   = [t for t in all_trips if t.start_date and t.end_date and t.start_date <= today <= t.end_date]
    upcoming  = [t for t in all_trips if t.start_date and t.start_date > today]
    completed = [t for t in all_trips if t.end_date and t.end_date < today]
    no_dates  = [t for t in all_trips if not t.start_date]

    return render_template('trips/list.html', trips=all_trips,
                           ongoing=ongoing, upcoming=upcoming,
                           completed=completed, no_dates=no_dates, q=q)


@trips_bp.route('/trips/create', methods=['GET', 'POST'])
@login_required
def create_trip():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        start_str = request.form.get('start_date', '')
        end_str = request.form.get('end_date', '')
        cover_photo = request.form.get('cover_photo', '').strip()

        if not name:
            flash('Trip name is required.', 'error')
            return render_template('trips/create.html')

        start_date = datetime.strptime(start_str, '%Y-%m-%d').date() if start_str else None
        end_date = datetime.strptime(end_str, '%Y-%m-%d').date() if end_str else None

        trip = Trip(user_id=current_user.id, name=name, description=description,
                    start_date=start_date, end_date=end_date, cover_photo=cover_photo)
        db.session.add(trip)
        db.session.commit()

        send_trip_created(current_user.email, current_user.name.split()[0], trip)

        flash('Trip created! Now build your itinerary.', 'success')
        return redirect(url_for('trips.builder', trip_id=trip.id))
    return render_template('trips/create.html')


@trips_bp.route('/trips/<int:trip_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_trip(trip_id):
    trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first_or_404()
    if request.method == 'POST':
        trip.name = request.form.get('name', trip.name).strip()
        trip.description = request.form.get('description', '').strip()
        start_str = request.form.get('start_date', '')
        end_str = request.form.get('end_date', '')
        trip.cover_photo = request.form.get('cover_photo', '').strip()
        if start_str:
            trip.start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
        if end_str:
            trip.end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
        db.session.commit()
        flash('Trip updated.', 'success')
        return redirect(url_for('trips.view_trip', trip_id=trip.id))
    return render_template('trips/create.html', trip=trip)


@trips_bp.route('/trips/<int:trip_id>/delete', methods=['POST'])
@login_required
def delete_trip(trip_id):
    trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first_or_404()
    db.session.delete(trip)
    db.session.commit()
    flash('Trip deleted.', 'success')
    return redirect(url_for('trips.my_trips'))


@trips_bp.route('/trips/<int:trip_id>')
@login_required
def view_trip(trip_id):
    from datetime import timedelta
    trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first_or_404()
    calendar_days = []
    if trip.start_date and trip.end_date:
        d = trip.start_date
        while d <= trip.end_date:
            current_stop = None
            for stop in trip.stops:
                if stop.arrival_date and stop.departure_date:
                    if stop.arrival_date <= d <= stop.departure_date:
                        current_stop = stop
                        break
            calendar_days.append({
                'date': d,
                'day_num': (d - trip.start_date).days + 1,
                'stop': current_stop,
            })
            d += timedelta(days=1)
    return render_template('trips/view.html', trip=trip, calendar_days=calendar_days)


@trips_bp.route('/trips/<int:trip_id>/builder')
@login_required
def builder(trip_id):
    trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first_or_404()
    categories = db.session.query(Activity.category).distinct().order_by(Activity.category).all()
    categories = [c[0] for c in categories if c[0]]
    return render_template('trips/builder.html', trip=trip, categories=categories)


@trips_bp.route('/trips/<int:trip_id>/stops', methods=['POST'])
@login_required
def add_stop(trip_id):
    trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first_or_404()
    city_id = request.form.get('city_id', type=int)
    arrival_str = request.form.get('arrival_date', '')
    departure_str = request.form.get('departure_date', '')

    if not city_id:
        flash('Please select a city.', 'error')
        return redirect(url_for('trips.builder', trip_id=trip_id))

    city = City.query.get_or_404(city_id)
    max_order = db.session.query(db.func.max(Stop.order_index))\
                          .filter_by(trip_id=trip_id).scalar() or 0
    arrival = datetime.strptime(arrival_str, '%Y-%m-%d').date() if arrival_str else None
    departure = datetime.strptime(departure_str, '%Y-%m-%d').date() if departure_str else None

    stop = Stop(trip_id=trip_id, city_id=city_id,
                arrival_date=arrival, departure_date=departure,
                order_index=max_order + 1)
    db.session.add(stop)
    db.session.commit()
    flash(f'{city.name} added to your itinerary.', 'success')
    return redirect(url_for('trips.builder', trip_id=trip_id))


@trips_bp.route('/stops/<int:stop_id>/delete', methods=['POST'])
@login_required
def delete_stop(stop_id):
    stop = Stop.query.get_or_404(stop_id)
    trip = Trip.query.filter_by(id=stop.trip_id, user_id=current_user.id).first_or_404()
    db.session.delete(stop)
    db.session.commit()
    flash('Stop removed.', 'success')
    return redirect(url_for('trips.builder', trip_id=trip.id))


@trips_bp.route('/stops/<int:stop_id>/activities', methods=['POST'])
@login_required
def add_activity(stop_id):
    stop = Stop.query.get_or_404(stop_id)
    Trip.query.filter_by(id=stop.trip_id, user_id=current_user.id).first_or_404()
    activity_id = request.form.get('activity_id', type=int)
    if not activity_id:
        return jsonify({'error': 'No activity selected'}), 400
    already = StopActivity.query.filter_by(stop_id=stop_id, activity_id=activity_id).first()
    if already:
        return jsonify({'error': 'Activity already added'}), 400
    sa = StopActivity(stop_id=stop_id, activity_id=activity_id)
    db.session.add(sa)
    db.session.commit()
    return jsonify({'success': True, 'sa_id': sa.id,
                    'activity': sa.activity.name,
                    'cost': sa.activity.estimated_cost,
                    'category': sa.activity.category})


@trips_bp.route('/stop-activities/<int:sa_id>/delete', methods=['POST'])
@login_required
def remove_activity(sa_id):
    sa = StopActivity.query.get_or_404(sa_id)
    stop = Stop.query.get(sa.stop_id)
    Trip.query.filter_by(id=stop.trip_id, user_id=current_user.id).first_or_404()
    db.session.delete(sa)
    db.session.commit()
    return jsonify({'success': True})


@trips_bp.route('/stops/reorder', methods=['POST'])
@login_required
def reorder_stops():
    order = request.json.get('order', [])
    for idx, stop_id in enumerate(order):
        stop = Stop.query.get(stop_id)
        if stop:
            trip = Trip.query.filter_by(id=stop.trip_id, user_id=current_user.id).first()
            if trip:
                stop.order_index = idx
    db.session.commit()
    return jsonify({'success': True})


# ── Packing Checklist ──────────────────────────────────────────────────────────

@trips_bp.route('/trips/<int:trip_id>/checklist')
@login_required
def checklist(trip_id):
    trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first_or_404()
    categories = ['clothing', 'documents', 'electronics', 'toiletries', 'other']
    items_by_cat = {cat: [i for i in trip.packing_items if i.category == cat]
                    for cat in categories}
    total = len(trip.packing_items)
    packed = sum(1 for i in trip.packing_items if i.is_packed)
    return render_template('checklist.html', trip=trip, items_by_cat=items_by_cat,
                           categories=categories, total=total, packed=packed)


@trips_bp.route('/trips/<int:trip_id>/checklist/add', methods=['POST'])
@login_required
def add_packing_item(trip_id):
    trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first_or_404()
    name = request.form.get('name', '').strip()
    category = request.form.get('category', 'other')
    if name:
        item = PackingItem(trip_id=trip.id, name=name, category=category)
        db.session.add(item)
        db.session.commit()
    return redirect(url_for('trips.checklist', trip_id=trip_id))


@trips_bp.route('/packing-items/<int:item_id>/toggle', methods=['POST'])
@login_required
def toggle_packing_item(item_id):
    item = PackingItem.query.get_or_404(item_id)
    Trip.query.filter_by(id=item.trip_id, user_id=current_user.id).first_or_404()
    item.is_packed = not item.is_packed
    db.session.commit()
    return jsonify({'is_packed': item.is_packed})


@trips_bp.route('/packing-items/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_packing_item(item_id):
    item = PackingItem.query.get_or_404(item_id)
    trip = Trip.query.filter_by(id=item.trip_id, user_id=current_user.id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('trips.checklist', trip_id=trip.id))


@trips_bp.route('/trips/<int:trip_id>/checklist/reset', methods=['POST'])
@login_required
def reset_checklist(trip_id):
    trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first_or_404()
    for item in trip.packing_items:
        item.is_packed = False
    db.session.commit()
    flash('Checklist reset — all items unmarked.', 'success')
    return redirect(url_for('trips.checklist', trip_id=trip_id))


@trips_bp.route('/trips/<int:trip_id>/checklist/toggle-all', methods=['POST'])
@login_required
def toggle_all_packed(trip_id):
    trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first_or_404()
    category = request.form.get('category', '')
    packed = request.form.get('packed', 'true') == 'true'
    items = [i for i in trip.packing_items if i.category == category] if category else trip.packing_items
    for item in items:
        item.is_packed = packed
    db.session.commit()
    return jsonify({'success': True})


# ── Notes ─────────────────────────────────────────────────────────────────────

@trips_bp.route('/trips/<int:trip_id>/notes')
@login_required
def notes(trip_id):
    trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first_or_404()
    all_notes = TripNote.query.filter_by(trip_id=trip_id)\
                              .order_by(TripNote.created_at.desc()).all()
    return render_template('notes.html', trip=trip, notes=all_notes)


@trips_bp.route('/trips/<int:trip_id>/notes/add', methods=['POST'])
@login_required
def add_note(trip_id):
    trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first_or_404()
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    stop_id = request.form.get('stop_id', type=int)
    if content:
        note = TripNote(trip_id=trip.id, title=title, content=content,
                        stop_id=stop_id if stop_id else None)
        db.session.add(note)
        db.session.commit()
        flash('Note saved.', 'success')
    return redirect(url_for('trips.notes', trip_id=trip_id))


@trips_bp.route('/notes/<int:note_id>/delete', methods=['POST'])
@login_required
def delete_note(note_id):
    note = TripNote.query.get_or_404(note_id)
    trip = Trip.query.filter_by(id=note.trip_id, user_id=current_user.id).first_or_404()
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for('trips.notes', trip_id=trip.id))


@trips_bp.route('/notes/<int:note_id>/edit', methods=['POST'])
@login_required
def edit_note(note_id):
    from flask import jsonify
    note = TripNote.query.get_or_404(note_id)
    Trip.query.filter_by(id=note.trip_id, user_id=current_user.id).first_or_404()
    note.title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    if content:
        note.content = content
        db.session.commit()
    return redirect(url_for('trips.notes', trip_id=note.trip_id))


# ── Email Itinerary ───────────────────────────────────────────────────────────

@trips_bp.route('/trips/<int:trip_id>/email', methods=['POST'])
@login_required
def email_itinerary(trip_id):
    trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first_or_404()
    to_email = request.form.get('email', '').strip() or current_user.email
    ok, msg = send_trip_summary(to_email, current_user.name.split()[0], trip)
    flash(msg, 'success' if ok else 'error')
    return redirect(url_for('trips.view_trip', trip_id=trip_id))


@trips_bp.route('/trips/<int:trip_id>/finish', methods=['POST'])
@login_required
def finish_trip(trip_id):
    from flask import session
    trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first_or_404()
    sent_key = f'emailed_trip_{trip_id}'
    if not session.get(sent_key) and trip.stops:
        ok, msg = send_trip_summary(current_user.email, current_user.name.split()[0], trip)
        if ok:
            session[sent_key] = True
            flash(f'✈️ Itinerary emailed to {current_user.email}!', 'success')
        else:
            flash(f'Could not send email: {msg}', 'error')
    return redirect(url_for('trips.view_trip', trip_id=trip_id))
