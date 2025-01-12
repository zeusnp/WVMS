from app import app, db, User

with app.app_context():
    # Drop all tables
    db.drop_all()
    
    # Create all tables
    db.create_all()
    
    # Create admin user
    admin = User(username='admin', password='admin123', is_admin=True)
    db.session.add(admin)
    db.session.commit()
    
    print("Database recreated and admin user created successfully!")
