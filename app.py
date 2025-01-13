from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import os
import sys
import logging
from functools import wraps
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Load environment variables
load_dotenv()

# Secret Key Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback_secret_key_for_development')

# Database Configuration
def configure_database(app):
    # Determine database URL
    if os.environ.get('FLASK_ENV') == 'production':
        database_url = os.environ.get('DATABASE_URL')
        
        if not database_url:
            logger.warning("DATABASE_URL not found. Falling back to SQLite.")
            database_url = 'sqlite:///production.db'
        
        # Handle Render's PostgreSQL URL
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
    else:
        # Development environment
        database_url = 'sqlite:///development.db'
    
    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Connection pooling and timeout settings
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 30,
        'pool_recycle': 3600,
    }
    
    logger.info(f"Database configured with URL: {database_url}")
    return database_url

# Configure database
database_url = configure_database(app)

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize extensions
try:
    print("Successfully initialized SQLAlchemy")
except Exception as e:
    print(f"Error initializing SQLAlchemy: {str(e)}")
    sys.exit(1)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import pandas after app initialization
try:
    import pandas as pd
    print("Successfully imported pandas")
except ImportError as e:
    print(f"Warning: Failed to import pandas: {str(e)}")
    pd = None

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need administrator privileges to access this page.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

# Vehicle Model
class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    vehicle_no = db.Column(db.String(50), nullable=False)
    party_name = db.Column(db.String(100), nullable=False)
    sub_party_name = db.Column(db.String(100))
    vehicle_fare = db.Column(db.Float, nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=False)
    measurement = db.relationship('Measurement', backref='vehicle', uselist=False)

    @property
    def is_measured(self):
        return self.measurement is not None

# Measurement Model
class Measurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    grade_a = db.Column(db.Float, nullable=False)
    grade_b = db.Column(db.Float, nullable=False)
    grade_c = db.Column(db.Float, nullable=False)
    grade_d = db.Column(db.Float, nullable=False)
    total_grade = db.Column(db.Float, nullable=False)
    pcs = db.Column(db.Integer, nullable=False)
    mix_total = db.Column(db.Float, nullable=False)
    six_futta = db.Column(db.Float, nullable=False)
    pcs_count = db.Column(db.Integer, nullable=False)
    remarks = db.Column(db.Text)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def dashboard():
    # Get basic statistics
    total_vehicles = Vehicle.query.count()
    today = datetime.now().date()
    measured_today = Vehicle.query.join(Measurement).filter(
        db.func.date(Vehicle.date) == today
    ).count()
    pending_measurements = Vehicle.query.filter(
        ~Vehicle.id.in_(db.session.query(Measurement.vehicle_id))
    ).count()

    # Get grade summaries
    grade_summary = db.session.query(
        db.func.sum(Measurement.grade_a).label('total_grade_a'),
        db.func.sum(Measurement.grade_b).label('total_grade_b'),
        db.func.sum(Measurement.grade_c).label('total_grade_c'),
        db.func.sum(Measurement.grade_d).label('total_grade_d'),
        db.func.sum(Measurement.total_grade).label('total_grade')
    ).first()

    # Get top parties by total grade
    top_parties = db.session.query(
        Vehicle.party_name,
        db.func.sum(Measurement.total_grade).label('total')
    ).join(Measurement).group_by(Vehicle.party_name)\
    .order_by(db.func.sum(Measurement.total_grade).desc())\
    .limit(5).all()

    # Get recent vehicles
    recent_vehicles = Vehicle.query.order_by(Vehicle.date.desc()).limit(10).all()

    # Format the data
    grade_data = {
        'Grade A': float(grade_summary.total_grade_a or 0),
        'Grade B': float(grade_summary.total_grade_b or 0),
        'Grade C': float(grade_summary.total_grade_c or 0),
        'Grade D': float(grade_summary.total_grade_d or 0)
    }

    return render_template('dashboard.html',
        total_vehicles=total_vehicles,
        measured_today=measured_today,
        pending_measurements=pending_measurements,
        total_grade=float(grade_summary.total_grade or 0),
        grade_data=grade_data,
        top_parties=top_parties,
        recent_vehicles=recent_vehicles
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/users', methods=['GET'])
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/add_user', methods=['POST'])
@login_required
@admin_required
def add_user():
    username = request.form.get('username')
    password = request.form.get('password')
    is_admin = request.form.get('is_admin') == 'on'
    
    if User.query.filter_by(username=username).first():
        flash('Username already exists', 'error')
        return redirect(url_for('users'))
    
    user = User(username=username, password=password, is_admin=is_admin)
    db.session.add(user)
    db.session.commit()
    flash('User added successfully')
    return redirect(url_for('users'))

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    if current_user.id == user_id:
        return jsonify({'error': 'Cannot delete your own account'}), 400
        
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})

@app.route('/reset_password/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def reset_password(user_id):
    if current_user.id == user_id:
        return jsonify({'error': 'Cannot reset your own password'}), 400
        
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    user.password = data.get('password')
    db.session.commit()
    return jsonify({'message': 'Password reset successfully'})

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'GET':
        return render_template('edit_profile.html', user=current_user)
        
    # Handle POST request
    try:
        # Get form data
        username = request.form.get('username')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Verify current password
        if not current_user.password == current_password:
            flash('Current password is incorrect', 'error')
            return redirect(url_for('edit_profile'))
        
        # Check if username already exists (except for current user)
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != current_user.id:
            flash('Username already exists', 'error')
            return redirect(url_for('edit_profile'))
        
        # Validate new password
        if new_password:
            if not confirm_password:
                flash('Please confirm your new password', 'error')
                return redirect(url_for('edit_profile'))
            if new_password != confirm_password:
                flash('New passwords do not match', 'error')
                return redirect(url_for('edit_profile'))
            current_user.password = new_password
        
        # Update username
        current_user.username = username
        
        # Save changes
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating profile: {str(e)}', 'error')
        return redirect(url_for('edit_profile'))

@app.route('/vehicles', methods=['GET', 'POST'])
@login_required
def vehicles():
    if request.method == 'POST':
        try:
            new_vehicle = Vehicle(
                date=datetime.strptime(request.form['date'], '%Y-%m-%d'),
                vehicle_no=request.form['vehicle_no'],
                party_name=request.form['party_name'],
                sub_party_name=request.form['sub_party_name'],
                vehicle_fare=float(request.form['vehicle_fare']),
                vehicle_type=request.form['vehicle_type']
            )
            db.session.add(new_vehicle)
            db.session.commit()
            flash('Vehicle added successfully', 'success')
            return redirect(url_for('vehicles'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding vehicle: {str(e)}', 'error')
            return redirect(url_for('vehicles'))

    # Get search parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    party_name = request.args.get('party_name')
    vehicle_type = request.args.get('vehicle_type')

    # Build query
    query = Vehicle.query

    if start_date:
        query = query.filter(Vehicle.date >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(Vehicle.date <= datetime.strptime(end_date, '%Y-%m-%d'))
    if party_name:
        query = query.filter(Vehicle.party_name.ilike(f'%{party_name}%'))
    if vehicle_type:
        query = query.filter(Vehicle.vehicle_type == vehicle_type)

    # Get results
    vehicles = query.order_by(Vehicle.date.desc()).all()
    return render_template('vehicles.html', vehicles=vehicles)

@app.route('/delete_vehicle/<int:vehicle_id>', methods=['POST'])
@login_required
@admin_required
def delete_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.measurement:
        db.session.delete(vehicle.measurement)
    db.session.delete(vehicle)
    db.session.commit()
    flash('Vehicle deleted successfully')
    return redirect(url_for('vehicles'))

@app.route('/measurements/<int:vehicle_id>', methods=['GET', 'POST'])
@login_required
def measurements(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    if request.method == 'POST':
        try:
            # Check if measurement already exists
            existing_measurement = Measurement.query.filter_by(vehicle_id=vehicle_id).first()
            if existing_measurement:
                flash('Measurement already exists for this vehicle', 'error')
                return redirect(url_for('measurements', vehicle_id=vehicle_id))

            # Calculate total grade
            grade_a = float(request.form['grade_a'])
            grade_b = float(request.form['grade_b'])
            grade_c = float(request.form['grade_c'])
            grade_d = float(request.form['grade_d'])
            total_grade = grade_a + grade_b + grade_c + grade_d

            new_measurement = Measurement(
                vehicle_id=vehicle_id,
                grade_a=grade_a,
                grade_b=grade_b,
                grade_c=grade_c,
                grade_d=grade_d,
                total_grade=total_grade,
                pcs=int(request.form['pcs']),
                mix_total=float(request.form['mix_total']),
                six_futta=float(request.form['six_futta']),
                pcs_count=int(request.form['pcs_count']),
                remarks=request.form.get('remarks', '')
            )
            db.session.add(new_measurement)
            db.session.commit()
            flash('Measurement added successfully', 'success')
            return redirect(url_for('vehicles'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding measurement: {str(e)}', 'error')
            return redirect(url_for('measurements', vehicle_id=vehicle_id))

    measurement = Measurement.query.filter_by(vehicle_id=vehicle_id).first()
    return render_template('measurements.html', vehicle=vehicle, measurement=measurement)

@app.route('/delete_measurement/<int:vehicle_id>', methods=['POST'])
@login_required
@admin_required
def delete_measurement(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.measurement:
        db.session.delete(vehicle.measurement)
        db.session.commit()
        flash('Measurement deleted successfully')
    return redirect(url_for('vehicles'))

@app.route('/get_measurement/<int:vehicle_id>')
@login_required
def get_measurement(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.measurement:
        measurement = vehicle.measurement
        return jsonify({
            'grade_a': measurement.grade_a,
            'grade_b': measurement.grade_b,
            'grade_c': measurement.grade_c,
            'grade_d': measurement.grade_d,
            'total_grade': measurement.total_grade,
            'pcs': measurement.pcs,
            'mix_total': measurement.mix_total,
            'six_futta': measurement.six_futta,
            'pcs_count': measurement.pcs_count,
            'remarks': measurement.remarks
        })
    return jsonify({'error': 'No measurement found'}), 404

@app.route('/export')
@login_required
def export_data():
    vehicles = Vehicle.query.all()
    
    # Create DataFrame
    data = []
    for vehicle in vehicles:
        measurement = vehicle.measurement
        row = {
            'Date': vehicle.date.strftime('%Y-%m-%d'),
            'Vehicle No': vehicle.vehicle_no,
            'Party Name': vehicle.party_name,
            'Sub Party Name': vehicle.sub_party_name,
            'Vehicle Fare': vehicle.vehicle_fare,
            'Vehicle Type': vehicle.vehicle_type,
            'Status': 'Measured' if vehicle.is_measured else 'Pending'
        }
        
        if measurement:
            row.update({
                'Grade A': measurement.grade_a,
                'Grade B': measurement.grade_b,
                'Grade C': measurement.grade_c,
                'Grade D': measurement.grade_d,
                'Total Grade': measurement.total_grade,
                'PCS': measurement.pcs,
                'Mix Total': measurement.mix_total,
                '6 Futta': measurement.six_futta,
                'PCS Count': measurement.pcs_count,
                'Remarks': measurement.remarks
            })
        else:
            row.update({
                'Grade A': '-',
                'Grade B': '-',
                'Grade C': '-',
                'Grade D': '-',
                'Total Grade': '-',
                'PCS': '-',
                'Mix Total': '-',
                '6 Futta': '-',
                'PCS Count': '-',
                'Remarks': '-'
            })
        
        data.append(row)
    
    if pd is not None:
        df = pd.DataFrame(data)
        output = 'vehicles_report.xlsx'
        df.to_excel(output, index=False)
        return send_file(output, as_attachment=True, download_name='vehicles_report.xlsx')
    else:
        return jsonify({'error': 'Failed to export data'}), 500

if __name__ == '__main__':
    try:
        with app.app_context():
            print("Creating database tables...")
            db.create_all()
            print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating database tables: {str(e)}")
        sys.exit(1)

    # Only enable debug mode in development
    debug = os.environ.get('FLASK_ENV') != 'production'
    port = int(os.environ.get('PORT', 5000))
    
    print(f"Starting server on port {port} with debug={debug}")
    app.run(host='0.0.0.0', port=port, debug=debug)
