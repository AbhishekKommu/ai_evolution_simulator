import os
from flask import Flask
from config import Config
from models import db
from routes.auth import auth_bp
from routes.game import game_bp
from routes.leaderboard import leaderboard_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure database directory exists
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    db.init_app(app)

    # ✅ Make session available in all templates
    @app.context_processor
    def inject_session():
        from flask import session
        return dict(session=session)

    app.register_blueprint(auth_bp)
    app.register_blueprint(game_bp)
    app.register_blueprint(leaderboard_bp)

    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)