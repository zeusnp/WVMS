from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import pandas as pd
import os
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')

# Database configuration
if os.environ.get('FLASK_ENV') == 'production':
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///wvms.db')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wvms.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

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
    # Get grade summaries
    grade_summary = db.session.query(
        db.func.sum(Measurement.grade_a).label('total_grade_a'),
        db.func.sum(Measurement.grade_b).label('total_grade_b'),
        db.func.sum(Measurement.grade_c).label('total_grade_c'),
        db.func.sum(Measurement.grade_d).label('total_grade_d')
    ).first()

    # Get top parties by total grade
    top_parties = db.session.query(
        Vehicle.party_name,
        db.func.sum(Measurement.total_grade).label('total')
    ).join(Measurement).group_by(Vehicle.party_name)\
    .order_by(db.func.sum(Measurement.total_grade).desc())\
    .limit(5).all()

    # Format the data
    grade_data = {
        'Grade A': float(grade_summary.total_grade_a or 0),
        'Grade B': float(grade_summary.total_grade_b or 0),
        'Grade C': float(grade_summary.total_grade_c or 0),
        'Grade D': float(grade_summary.total_grade_d or 0)
    }

    party_data = [
        {'name': party.party_name, 'total': float(party.total)}
        for party in top_parties
    ]

    total_vehicles = Vehicle.query.count()
    measured_vehicles = Measurement.query.count()
    vehicles_left = total_vehicles - measured_vehicles

    return render_template('dashboard.html', 
                         grade_data=grade_data,
                         party_data=party_data,
                         total_vehicles=total_vehicles, 
                         vehicles_left=vehicles_left)

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

@app.route('/edit_profile', methods=['POST'])
@login_required
@admin_required
def edit_profile():
    # Get form data
    username = request.form.get('username')
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    
    # Verify current password
    if not current_user.password == current_password:
        flash('Current password is incorrect', 'error')
        return redirect(url_for('users'))
    
    # Check if username already exists (except for current user)
    existing_user = User.query.filter_by(username=username).first()
    if existing_user and existing_user.id != current_user.id:
        flash('Username already exists', 'error')
        return redirect(url_for('users'))
    
    # Update username
    current_user.username = username
    
    # Update password if provided
    if new_password:
        current_user.password = new_password
    
    db.session.commit()
    flash('Profile updated successfully')
    return redirect(url_for('users'))

@app.route('/vehicles', methods=['GET', 'POST'])
@login_required
def vehicles():
    if request.method == 'POST':
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
        flash('Vehicle added successfully')
        return redirect(url_for('vehicles'))
    
    vehicles = Vehicle.query.all()
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
        if vehicle.measurement:
            flash('Measurement already exists for this vehicle')
            return redirect(url_for('vehicles'))
            
        measurement = Measurement(
            vehicle_id=vehicle_id,
            grade_a=float(request.form['grade_a']),
            grade_b=float(request.form['grade_b']),
            grade_c=float(request.form['grade_c']),
            grade_d=float(request.form['grade_d']),
            total_grade=float(request.form['total_grade']),
            pcs=int(request.form['pcs']),
            mix_total=float(request.form['mix_total']),
            six_futta=float(request.form['six_futta']),
            pcs_count=int(request.form['pcs_count']),
            remarks=request.form['remarks']
        )
        db.session.add(measurement)
        db.session.commit()
        flash('Measurement added successfully')
        return redirect(url_for('vehicles'))
    
    if vehicle.measurement:
        flash('Measurement already exists for this vehicle')
        return redirect(url_for('vehicles'))
    
    return render_template('measurements.html', vehicle=vehicle)

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
    
    df = pd.DataFrame(data)
    
    # Export to Excel
    output = 'vehicles_report.xlsx'
    df.to_excel(output, index=False)
    return send_file(output, as_attachment=True, download_name='vehicles_report.xlsx')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
