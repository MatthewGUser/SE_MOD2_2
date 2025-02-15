import os
from app import create_app, db
from config import config
from app.models import User, Mechanic, ServiceTicket

# Use production config for Gunicorn, development for local
env = 'production' if os.getenv('GUNICORN_CMD_ARGS') else 'development'
app = create_app('production')

if __name__ == '__main__':
    print(f"Running in {os.getenv('FLASK_ENV', 'dev')} mode")
    app.run(debug=True, port=5000)

# Register CLI commands
@app.cli.command("init-db")
def init_db():
    """Initialize the database."""
    from app import db
    with app.app_context():
        db.create_all()
        print('Database initialized!')