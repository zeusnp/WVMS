from app import app, db, User
from datetime import datetime
import sys

def init_db():
    try:
        with app.app_context():
            # Create all tables
            print("Creating database tables...")
            db.create_all()
            print("Database tables created successfully!")
            
            # Check if admin user exists
            print("Checking for admin user...")
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                print("Creating admin user...")
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
                    sys.exit(1)
            else:
                print("Admin user already exists!")
            
            print("Database initialization completed successfully!")
            return True
            
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    print("Starting database initialization...")
    init_db()
