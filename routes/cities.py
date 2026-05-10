from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import db, City, Activity, Trip

cities_bp = Blueprint('cities', __name__)


@cities_bp.route('/explore')
@login_required
def search_page():
    query = request.args.get('q', '')
    region = request.args.get('region', '')
    cost_tier = request.args.get('cost_tier', '')
    cities = City.query
    if query:
        cities = cities.filter(City.name.ilike(f'%{query}%'))
    if region:
        cities = cities.filter_by(region=region)
    if cost_tier == 'budget':
        cities = cities.filter(City.cost_index < 40)
    elif cost_tier == 'mid':
        cities = cities.filter(City.cost_index >= 40, City.cost_index < 70)
    elif cost_tier == 'luxury':
        cities = cities.filter(City.cost_index >= 70)
    cities = cities.order_by(City.popularity.desc()).all()
    regions = db.session.query(City.region).distinct().order_by(City.region).all()
    regions = [r[0] for r in regions if r[0]]
    user_trips = Trip.query.filter_by(user_id=current_user.id).order_by(Trip.created_at.desc()).all()
    return render_template('explore.html', cities=cities, query=query,
                           selected_region=region, selected_cost=cost_tier,
                           regions=regions, user_trips=user_trips)


@cities_bp.route('/api/cities')
@login_required
def api_cities():
    q = request.args.get('q', '').strip()
    region = request.args.get('region', '').strip()
    cost_tier = request.args.get('cost_tier', '').strip()
    cities = City.query
    if q:
        cities = cities.filter(
            db.or_(City.name.ilike(f'%{q}%'), City.country.ilike(f'%{q}%'))
        )
    if region:
        cities = cities.filter_by(region=region)
    if cost_tier == 'budget':
        cities = cities.filter(City.cost_index < 40)
    elif cost_tier == 'mid':
        cities = cities.filter(City.cost_index >= 40, City.cost_index < 70)
    elif cost_tier == 'luxury':
        cities = cities.filter(City.cost_index >= 70)
    cities = cities.order_by(City.popularity.desc()).limit(50).all()
    return jsonify([{
        'id': c.id, 'name': c.name, 'country': c.country,
        'region': c.region, 'cost_index': c.cost_index,
        'popularity': c.popularity, 'image_url': c.image_url,
        'description': c.description,
        'activity_count': len(c.activities)
    } for c in cities])


@cities_bp.route('/api/activities')
@login_required
def api_activities():
    city_id = request.args.get('city_id', type=int)
    category = request.args.get('category', '')
    q = request.args.get('q', '').strip()
    cost_tier = request.args.get('cost_tier', '')
    duration_tier = request.args.get('duration_tier', '')
    activities = Activity.query
    if city_id:
        activities = activities.filter_by(city_id=city_id)
    if category:
        activities = activities.filter_by(category=category)
    if q:
        activities = activities.filter(Activity.name.ilike(f'%{q}%'))
    if cost_tier == 'free':
        activities = activities.filter(Activity.estimated_cost == 0)
    elif cost_tier == 'budget':
        activities = activities.filter(Activity.estimated_cost > 0, Activity.estimated_cost <= 20)
    elif cost_tier == 'mid':
        activities = activities.filter(Activity.estimated_cost > 20, Activity.estimated_cost <= 60)
    elif cost_tier == 'premium':
        activities = activities.filter(Activity.estimated_cost > 60)
    if duration_tier == 'short':
        activities = activities.filter(Activity.duration_hours < 2)
    elif duration_tier == 'half':
        activities = activities.filter(Activity.duration_hours >= 2, Activity.duration_hours <= 4)
    elif duration_tier == 'full':
        activities = activities.filter(Activity.duration_hours > 4)
    activities = activities.order_by(Activity.estimated_cost).limit(40).all()
    return jsonify([{
        'id': a.id, 'name': a.name, 'description': a.description,
        'category': a.category, 'estimated_cost': a.estimated_cost,
        'duration_hours': a.duration_hours, 'image_url': a.image_url
    } for a in activities])
