#!/usr/bin/env bash

# exit on error
set -o errexit

echo "Starting build process..."

# Install python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
sleep 15

# Check if DATABASE_URL is set
if [ -z "${DATABASE_URL}" ]; then
    echo "WARNING: DATABASE_URL is not set!"
    echo "This might be normal during the initial build. The database will be configured later."
else
    echo "DATABASE_URL is properly set."
fi

# Initialize the database
echo "Starting database initialization..."
python <<EOF
from app import app, db
from init_db import init_db
import time
import os

print("Checking database configuration...")
db_url = os.environ.get('DATABASE_URL', 'Not Set')
print(f"Database URL status: {'Set' if db_url != 'Not Set' else 'Not Set'}")

print("Creating database tables...")
with app.app_context():
    try:
        db.create_all()
        print("Database tables created successfully!")
        
        # Run initialization
        success = init_db()
        if success:
            print("Database initialization completed!")
        else:
            print("Database initialization failed!")
            exit(1)
    except Exception as e:
        print(f"Error during database setup: {str(e)}")
        exit(1)
EOF

echo "Build process completed!"
