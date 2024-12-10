from app import app
from models import create_initial_data

with app.app_context():
    create_initial_data()
    print("Initial data created successfully!")
