from app import app, db, User
from datetime import datetime

def init_db():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Create admin user
            admin = User(
                username='admin',
                password='admin',
                is_admin=True
            )
            db.session.add(admin)
            try:
                db.session.commit()
                print("Admin user created successfully!")
            except Exception as e:
                db.session.rollback()
                print(f"Error creating admin user: {str(e)}")

if __name__ == '__main__':
    print("Initializing database...")
    init_db()
    print("Database initialization completed!")
