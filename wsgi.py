from app import create_app

# Create app with production config for Gunicorn
app = create_app('production')

if __name__ == '__main__':
    app.run()