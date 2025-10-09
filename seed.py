from models.quiz import db, db_add_test_data
from app import create_app

app = create_app()
with app.app_context():
    db_add_test_data()
    print("Test data seeded")