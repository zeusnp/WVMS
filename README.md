# Wood Carrying Vehicle Management System (WVMS)

A comprehensive system for managing wood carrying vehicles, including vehicle tracking, measurements, and user management.

## Features

- User Authentication and Authorization
  - Admin-only access to user management
  - Secure login system
  
- Dashboard
  - Overview of total vehicles
  - Vehicles left to measure
  - Quick access to main functions
  
- Vehicle Management
  - Add new vehicles with details
  - Record vehicle measurements
  - Sort and filter vehicle data
  
- Measurement Recording
  - Grade-wise measurement recording (A, B, C, D)
  - Automatic total calculation
  - Additional measurements (PCS, Mix Total, 6 Futta)
  
- Data Export
  - Export to Excel
  - Export to PDF
  - Customizable data sorting

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
```

5. Create an admin user:
```python
>>> from app import User
>>> admin = User(username='admin', password='admin123', is_admin=True)
>>> db.session.add(admin)
>>> db.session.commit()
```

6. Run the application:
```bash
python app.py
```

## Usage

1. Login with admin credentials
2. Add users through the User Management interface
3. Add vehicles and their details
4. Record measurements for vehicles
5. Export data as needed

## Security

- Only admin users can manage other users
- Passwords are stored securely
- Session management for authenticated users

## Requirements

- Python 3.7+
- Flask
- SQLAlchemy
- Other dependencies listed in requirements.txt
