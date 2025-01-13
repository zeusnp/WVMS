from app import app, db, User
import logging

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
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            
            logger.info("Database recreated and admin user created successfully!")
    
    except Exception as e:
        logger.error(f"Error recreating database: {e}")
        raise

if __name__ == '__main__':
    recreate_database()
