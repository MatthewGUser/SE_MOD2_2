import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from config import config
from app.models import User, Mechanic, ServiceTicket

def create_flask_app():
    """Factory function to create and configure the Flask application"""
    env = os.getenv('FLASK_ENV', 'prod')
    
    if env not in config:
        env = 'dev'
    
    app = create_app(config[env])
    
    with app.app_context():
        db.create_all()
    
    return app

app = create_flask_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)