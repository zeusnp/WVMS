from app import app, db, User
from datetime import datetime
import sys
import time

def init_db():
    max_retries = 5
    retry_delay = 2  # seconds

    for attempt in range(max_retries):
        try:
            print(f"Database initialization attempt {attempt + 1} of {max_retries}")
            
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
                        raise
                else:
                    print("Admin user already exists!")
                
                print("Database initialization completed successfully!")
                return True
                
        except Exception as e:
            print(f"Error during database initialization (attempt {attempt + 1}): {str(e)}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Maximum retry attempts reached. Database initialization failed.")
                sys.exit(1)

if __name__ == '__main__':
    print("Starting database initialization...")
    init_db()
