from app import create_app, db

# Create app instance with explicit environment
app = create_app('development')

@app.cli.command("init-db")
def init_db():
    """Initialize the database."""
    db.create_all()
    print('Database initialized!')

if __name__ == '__main__':
    # Use FLASK_ENV or default to development
    env = app.config.get('ENV', 'development')
    print(f"Running in {env} mode")
    app.run(debug=True)