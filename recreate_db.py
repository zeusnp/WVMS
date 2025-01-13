from app import app, db, User
import logging
import sys
import os
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('database_recreation.log')
    ]
)
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
        logger.error(f"Traceback: {traceback.format_exc()}")
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
                
                # Optional: Reset password if needed
                admin_password = os.environ.get('ADMIN_PASSWORD')
                if admin_password:
                    admin.set_password(admin_password)
                    db.session.commit()
                    logger.info("Admin password updated from environment variable.")
    
    except Exception as e:
        logger.error(f"Error verifying admin user: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

def list_users():
    try:
        with app.app_context():
            users = User.query.all()
            logger.info("Current users in the database:")
            for user in users:
                logger.info(f"Username: {user.username}, Admin: {user.is_admin}")
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

if __name__ == '__main__':
    # Choose the appropriate action based on environment
    env = os.environ.get('FLASK_ENV', 'development')
    
    if env == 'production':
        verify_admin_user()
        list_users()
    else:
        recreate_database()
        list_users()
