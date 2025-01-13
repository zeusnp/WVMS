from app import app, db, User
import logging
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def recreate_database():
    try:
        with app.app_context():
            # Drop all tables
            logger.info("Dropping existing tables...")
            db.drop_all()
            
            # Create all tables
            logger.info("Creating new tables...")
            db.create_all()
            
            # Create admin user
            recreate_admin_user()
            
            logger.info("Database recreated successfully!")
    
    except Exception as e:
        logger.error(f"Error recreating database: {e}")
        logger.error(f"Traceback: {sys.exc_info()}")
        raise

def recreate_admin_user():
    try:
        with app.app_context():
            # Check if admin user already exists
            existing_admin = User.query.filter_by(username='admin').first()
            
            if existing_admin:
                logger.info("Admin user already exists. Skipping creation.")
                return
            
            # Create admin user
            logger.info("Creating admin user...")
            admin = User(username='admin', is_admin=True)
            admin.set_password(os.environ.get('ADMIN_PASSWORD', 'admin123'))
            db.session.add(admin)
            db.session.commit()
            
            logger.info("Admin user created successfully!")
    
    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
        logger.error(f"Traceback: {sys.exc_info()}")
        raise

if __name__ == '__main__':
    recreate_database()
