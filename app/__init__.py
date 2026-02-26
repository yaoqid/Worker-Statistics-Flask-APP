import os
from flask import Flask, render_template, session
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize the database
db = SQLAlchemy()
# Initialize the migration
migrate = Migrate()

# Code is helped by ChatGPT
# Create the application factory
def create_app():
    app = Flask(__name__)

    # Database configuration
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(
        BASE_DIR, '..', 'data', 'night_worker_normalised.db'
    )
    # Configure the database URI
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key'

    # Ensure session expires when browser closes
    # Session is valid for 24 hours
    app.config['SESSION_PERMANENT'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(
        hours=24
    )
    # Store global state here
    app.config['FIRST_REQUEST_HANDLED'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    # Register global error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template(
            '404.html', message="Sorry, page not found!"
        ), 404

    # Register global error handlers
    @app.errorhandler(500)
    def internal_error(error):
        return render_template(
            '500.html',
            message="Internal server error, please try again later."
        ), 500

    # Import routes to ensure all routes are registered
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Use `app.config` to ensure `session.clear()` is executed only once
    @app.before_request
    def auto_logout_on_restart():
        """Clear all sessions once when Flask restarts (executed only once)"""
        # Check if this is the first request
        if not app.config['FIRST_REQUEST_HANDLED']:
            # Clear all sessions
            session.clear()
            # Set the flag to True
            app.config['FIRST_REQUEST_HANDLED'] = True

    # Ensure browser does not cache session
    @app.after_request
    def prevent_session_persistence(response):
        '''Prevent browser from caching session'''
        response.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, max-age=0"
        )
        response.headers["Expires"] = "0"
        response.headers["Pragma"] = "no-cache"
        return response

    return app
