from app import app, db, User
import os
import sys
import logging
import time
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_db():
    max_retries = 5
    retry_delay = 5  # seconds

    for attempt in range(max_retries):
        try:
            logger.info(f"Database initialization attempt {attempt + 1}")
            
            with app.app_context():
                # Check database URL
                database_url = os.environ.get('DATABASE_URL', 'Not Set')
                logger.info(f"Database URL: {database_url}")

                # Create all tables
                logger.info("Creating database tables...")
                db.create_all()
                logger.info("Database tables created successfully!")
                
                # Check if admin user exists
                logger.info("Checking for admin user...")
                admin = User.query.filter_by(username='admin').first()
                
                if not admin:
                    logger.info("Creating admin user...")
                    admin = User(
                        username='admin',
                        password='admin',  # Change this in production!
                        is_admin=True
                    )
                    db.session.add(admin)
                    
                    try:
                        db.session.commit()
                        logger.info("Admin user created successfully!")
                    except SQLAlchemyError as e:
                        db.session.rollback()
                        logger.error(f"Error creating admin user: {str(e)}")
                        raise
                else:
                    logger.info("Admin user already exists!")
                
                logger.info("Database initialization completed successfully!")
                return True
                
        except Exception as e:
            logger.error(f"Database initialization error (attempt {attempt + 1}): {str(e)}")
            
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.error("Maximum retry attempts reached. Database initialization failed.")
                
                # In production, don't exit - just log the error
                if os.environ.get('FLASK_ENV') == 'production':
                    logger.warning("Continuing in production mode despite initialization failure.")
                    return False
                else:
                    sys.exit(1)

if __name__ == '__main__':
    logger.info("Starting database initialization...")
    init_db()
