from app import app, db, User
from datetime import datetime
import sys
import time
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def init_db():
    max_retries = 5
    retry_delay = 5  # seconds

    for attempt in range(max_retries):
        try:
            logger.info(f"Database initialization attempt {attempt + 1} of {max_retries}")
            
            with app.app_context():
                # Wait for database to be ready in production
                if os.environ.get('FLASK_ENV') == 'production':
                    logger.info("Production environment detected, waiting for database...")
                    time.sleep(10)  # Give the database time to start
                
                # Create all tables
                logger.info("Creating database tables...")
                db.create_all()
                logger.info("Database tables created successfully!")
                
                # Check if admin user exists
                logger.info("Checking for admin user...")
                admin = User.query.filter_by(username='admin').first()
                if not admin:
                    logger.info("Creating admin user...")
                    # Create admin user
                    admin = User(
                        username='admin',
                        password='admin',
                        is_admin=True
                    )
                    db.session.add(admin)
                    try:
                        db.session.commit()
                        logger.info("Admin user created successfully!")
                    except Exception as e:
                        db.session.rollback()
                        logger.error(f"Error creating admin user: {str(e)}")
                        raise
                else:
                    logger.info("Admin user already exists!")
                
                logger.info("Database initialization completed successfully!")
                return True
                
        except Exception as e:
            logger.error(f"Error during database initialization (attempt {attempt + 1}): {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.error("Maximum retry attempts reached. Database initialization failed.")
                if os.environ.get('FLASK_ENV') != 'production':
                    sys.exit(1)
                else:
                    logger.warning("Production environment detected, continuing despite error...")
                    return False

if __name__ == '__main__':
    logger.info("Starting database initialization...")
    init_db()
