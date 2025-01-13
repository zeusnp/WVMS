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
            logger.info("Creating admin user...")
            admin = User(username='admin', is_admin=True)
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            
            logger.info("Database recreated and admin user created successfully!")
    
    except Exception as e:
        logger.error(f"Error recreating database: {e}")
        logger.error(f"Traceback: {sys.exc_info()}")
        raise

def verify_admin_user():
    try:
        with app.app_context():
            # Check if admin user exists
            admin = User.query.filter_by(username='admin').first()
            
            if not admin:
                logger.warning("No admin user found. Creating default admin...")
                admin = User(username='admin', is_admin=True)
                admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
                admin.set_password(admin_password)
                db.session.add(admin)
                db.session.commit()
                logger.info("Default admin user created.")
            else:
                logger.info("Admin user already exists.")
    
    except Exception as e:
        logger.error(f"Error verifying admin user: {e}")
        logger.error(f"Traceback: {sys.exc_info()}")
        raise

if __name__ == '__main__':
    # Choose the appropriate action based on environment
    if os.environ.get('FLASK_ENV') == 'production':
        verify_admin_user()
    else:
        recreate_database()
