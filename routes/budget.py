from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, Trip, BudgetItem, Stop, StopActivity

budget_bp = Blueprint('budget', __name__)

CATEGORIES = ['transport', 'stay', 'meals', 'activities', 'other']


@budget_bp.route('/trips/<int:trip_id>/budget')
@login_required
def budget(trip_id):
    trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first_or_404()

    activity_total = sum(
        (sa.custom_cost if sa.custom_cost is not None else sa.activity.estimated_cost)
        for stop in trip.stops for sa in stop.stop_activities
    )

    manual_by_cat = {cat: 0.0 for cat in CATEGORIES}
    for item in trip.budget_items:
        if item.category in manual_by_cat:
            manual_by_cat[item.category] += item.amount

    manual_by_cat['activities'] += activity_total
    grand_total = sum(manual_by_cat.values())
    avg_per_day = round(grand_total / trip.total_days, 2) if trip.total_days else 0

    budget_target = trip.budget_target or 0
    budget_pct = min(round((grand_total / budget_target) * 100, 1), 100) if budget_target > 0 else 0
    over_budget = budget_target > 0 and grand_total > budget_target

    # Per-stop breakdown with daily rate and over-budget flag
    daily_budget = round(budget_target / trip.total_days, 2) if budget_target and trip.total_days else 0
    stop_costs = []
    for s in trip.stops:
        daily_rate = round(s.activity_cost / s.days, 2) if s.days else 0
        stop_costs.append({
            'city': s.city.name,
            'country': s.city.country,
            'cost': round(s.activity_cost, 2),
            'days': s.days,
            'daily_rate': daily_rate,
            'over_budget': daily_budget > 0 and daily_rate > daily_budget,
            'activities': len(s.stop_activities),
        })

    return render_template('budget.html', trip=trip,
                           manual_by_cat=manual_by_cat,
                           grand_total=round(grand_total, 2),
                           avg_per_day=avg_per_day,
                           budget_target=budget_target,
                           budget_pct=budget_pct,
                           over_budget=over_budget,
                           daily_budget=daily_budget,
                           categories=CATEGORIES,
                           stop_costs=stop_costs)


@budget_bp.route('/trips/<int:trip_id>/budget/target', methods=['POST'])
@login_required
def set_budget_target(trip_id):
    trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first_or_404()
    target = request.form.get('budget_target', 0, type=float)
    trip.budget_target = target if target > 0 else None
    db.session.commit()
    flash('Budget target updated.', 'success')
    return redirect(url_for('budget.budget', trip_id=trip_id))


@budget_bp.route('/trips/<int:trip_id>/budget/add', methods=['POST'])
@login_required
def add_budget_item(trip_id):
    trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first_or_404()
    label = request.form.get('label', '').strip()
    amount = request.form.get('amount', 0, type=float)
    category = request.form.get('category', 'other')
    if label and amount > 0:
        item = BudgetItem(trip_id=trip.id, label=label, amount=amount, category=category)
        db.session.add(item)
        db.session.commit()
        flash('Expense added.', 'success')
    return redirect(url_for('budget.budget', trip_id=trip_id))


@budget_bp.route('/budget-items/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_budget_item(item_id):
    item = BudgetItem.query.get_or_404(item_id)
    trip = Trip.query.filter_by(id=item.trip_id, user_id=current_user.id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('budget.budget', trip_id=trip.id))


@budget_bp.route('/trips/<int:trip_id>/invoice')
@login_required
def invoice(trip_id):
    import datetime
    trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first_or_404()

    line_items = []
    for stop in trip.stops:
        for sa in stop.stop_activities:
            cost = sa.custom_cost if sa.custom_cost is not None else sa.activity.estimated_cost
            line_items.append({
                'category': sa.activity.category or 'activity',
                'description': f"{sa.activity.name} — {stop.city.name}",
                'qty': 1,
                'unit_cost': cost,
                'amount': cost,
            })
    for item in trip.budget_items:
        line_items.append({
            'category': item.category,
            'description': item.label,
            'qty': 1,
            'unit_cost': item.amount,
            'amount': item.amount,
        })

    grand_total = round(sum(i['amount'] for i in line_items), 2)
    invoice_num = f"TL-{trip.id:04d}-{datetime.date.today().strftime('%Y%m%d')}"

    return render_template('invoice.html', trip=trip, line_items=line_items,
                           grand_total=grand_total, invoice_num=invoice_num)
