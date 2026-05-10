from flask import Flask, render_template
from models import db
from flask_login import LoginManager
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from routes.auth import auth_bp
    from routes.trips import trips_bp
    from routes.cities import cities_bp
    from routes.budget import budget_bp
    from routes.share import share_bp
    from routes.profile import profile_bp
    from routes.admin import admin_bp
    from routes.community import community_bp
    from routes.chat import chat_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(trips_bp)
    app.register_blueprint(cities_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(share_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(community_bp)
    app.register_blueprint(chat_bp)

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    with app.app_context():
        db.create_all()
        migrations = [
            'ALTER TABLE trips ADD COLUMN budget_target FLOAT',
            'ALTER TABLE users ADD COLUMN phone VARCHAR(20)',
            'ALTER TABLE users ADD COLUMN city VARCHAR(100)',
            'ALTER TABLE users ADD COLUMN country VARCHAR(100)',
            'ALTER TABLE users ADD COLUMN bio TEXT',
        ]
        from sqlalchemy import text
        for sql in migrations:
            try:
                with db.engine.connect() as conn:
                    conn.execute(text(sql))
                    conn.commit()
            except Exception:
                pass

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
