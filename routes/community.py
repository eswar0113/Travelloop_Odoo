import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, CommunityPost, City, Trip

community_bp = Blueprint('community', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def _allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def _save_upload(file):
    """Save uploaded image, return public URL path or None."""
    if not file or file.filename == '':
        return None
    if not _allowed(file.filename):
        return None
    ext = secure_filename(file.filename).rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    file.save(os.path.join(upload_dir, unique_name))
    return url_for('static', filename=f'uploads/{unique_name}')


@community_bp.route('/community')
@login_required
def feed():
    q = request.args.get('q', '').strip()
    city_filter = request.args.get('city_id', type=int)

    query = CommunityPost.query.order_by(CommunityPost.created_at.desc())
    if q:
        query = query.filter(
            CommunityPost.title.ilike(f'%{q}%') | CommunityPost.content.ilike(f'%{q}%')
        )
    if city_filter:
        query = query.filter_by(city_id=city_filter)

    posts = query.limit(50).all()
    cities = City.query.order_by(City.name).all()
    user_trips = Trip.query.filter_by(user_id=current_user.id).order_by(Trip.created_at.desc()).all()

    return render_template('community.html', posts=posts, cities=cities,
                           q=q, city_filter=city_filter, user_trips=user_trips)


@community_bp.route('/community/post', methods=['POST'])
@login_required
def create_post():
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    city_id = request.form.get('city_id', type=int)
    trip_id = request.form.get('trip_id', type=int)

    if not title or not content:
        flash('Title and content are required.', 'error')
        return redirect(url_for('community.feed'))

    image_url = _save_upload(request.files.get('image'))

    post = CommunityPost(
        user_id=current_user.id,
        title=title,
        content=content,
        city_id=city_id or None,
        trip_id=trip_id or None,
        image_url=image_url,
    )
    db.session.add(post)
    db.session.commit()
    flash('Post shared with the community!', 'success')
    return redirect(url_for('community.feed'))


@community_bp.route('/community/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    post = CommunityPost.query.get_or_404(post_id)
    post.likes = (post.likes or 0) + 1
    db.session.commit()
    return redirect(request.referrer or url_for('community.feed'))


@community_bp.route('/community/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = CommunityPost.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        flash('You can only delete your own posts.', 'error')
        return redirect(url_for('community.feed'))
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'success')
    return redirect(url_for('community.feed'))
