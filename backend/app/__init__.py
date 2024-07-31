from flask import Flask
from flask_cors import CORS
from app.extensions import db, migrate
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize CORS
    CORS(app)
    
    # Register blueprints
    from app.views.user import user_bp
    from app.views.auth import auth_bp
    from app.views.funding_rates import funding_rates_bp
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(funding_rates_bp, url_prefix='/api/funding-rates')

    return app
