import warnings
import os
from sqlalchemy import exc as sa_exc

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_swagger_ui import get_swaggerui_blueprint
from datetime import timedelta
from config import config

# Suppress SQLAlchemy warnings
warnings.filterwarnings('ignore', category=sa_exc.SAWarning)

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
cache = Cache()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"  # Use in-memory storage instead of Redis
)

# API versioning
API_VERSION = 'v1'
API_PREFIX = f'/api/{API_VERSION}'

# Swagger configuration
SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI
API_URL = '/static/swagger.yml'  # Our API url (can of course be a local resource)

# Create Swagger UI blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Auto Shop API"
    }
)

def create_app(config_name='production'):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Use testing config when running tests
    if os.getenv('PYTEST_CURRENT_TEST'):
        config_name = 'testing'
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)
    
    with app.app_context():
        # Register blueprints with API versioning
        from app.components.blueprints.users import user_bp
        from app.components.blueprints.mechanics import mechanic_bp
        from app.components.blueprints.service_tickets import service_ticket_bp
        from app.components.blueprints.inventory import inventory_bp
        
        # Update blueprint registrations to match test expectations
        app.register_blueprint(user_bp, url_prefix='/users')
        app.register_blueprint(mechanic_bp, url_prefix='/mechanics')
        app.register_blueprint(service_ticket_bp, url_prefix='/service-tickets')  # Changed from /tickets
        app.register_blueprint(inventory_bp, url_prefix='/inventory')
        app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
        
        # Create database tables
        db.create_all()
    
    # JWT handlers
    @jwt.user_identity_loader
    def user_identity_lookup(identity):
        from app.models import User
        if isinstance(identity, User):
            return {
                'id': str(identity.id),
                'is_admin': identity.is_admin
            }
        return str(identity) if identity else None

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        try:
            identity = jwt_data["sub"]
            if isinstance(identity, dict):
                user_id = int(identity['id'])
            else:
                user_id = int(identity)
            from app.models import User
            # Updated to use Session.get()
            return db.session.get(User, user_id)
        except (ValueError, TypeError, KeyError):
            return None

    # Error handlers
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            "error": "Rate limit exceeded",
            "message": str(e.description)
        }), 429
    
    return app

# Create the application instance
app = create_app(os.getenv('FLASK_ENV', 'production'))