"""
Smart Hospital Management System
Backend Application using Flask
Created for Alexander Saji Varghese
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from flask import request, jsonify, session
import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime, date, timedelta
import hashlib
import os
from functools import wraps
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import json
import random
import string
from datetime import datetime, date, timedelta


app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads/lab_reports'

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'enter your password',  # Change this
    'database': 'hospital_db'
}

# Create uploads directory if not exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database Connection
def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Login Required Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Role-based access decorator
def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session or session['role'] not in allowed_roles:
                return jsonify({'error': 'Unauthorized access'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ==================== AUTHENTICATION ====================

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')
        user_captcha = data.get('captcha')

        real_captcha = session.get('captcha')

        # 🔐 CAPTCHA check
        if not real_captcha or user_captcha != real_captcha:
            return jsonify({'success': False, 'message': 'Invalid CAPTCHA'})
        
        user = None

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s AND status = 'Active'", 
                            (username, password))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user:
                session['user_id'] = user['user_id']
                session['username'] = user['username']
                session['role'] = user['role']
                session['full_name'] = user['full_name']
                session['patient_id'] = user['patient_id']
                return jsonify({'success': True, 'role': user['role']})
            else:
                return jsonify({'success': False, 'message': 'Invalid credentials'})
        
        return jsonify({'success': False, 'message': 'Database connection error'})
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ==================== DASHBOARD ====================

@app.route('/dashboard')
@login_required
def dashboard():
    role = session.get('role')
    return render_template('dashboard.html', role=role)

@app.route('/api/dashboard/stats')
@login_required
def dashboard_stats():
    conn = get_db_connection()
    stats = {}
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        # Total patients
        cursor.execute("SELECT COUNT(*) as count FROM patients WHERE status = 'Active'")
        stats['total_patients'] = cursor.fetchone()['count']
        
        # Today's appointments
        cursor.execute("SELECT COUNT(*) as count FROM appointments WHERE appointment_date = CURDATE() AND status != 'Cancelled'")
        stats['todays_appointments'] = cursor.fetchone()['count']
        
        # Active tokens
        cursor.execute("SELECT COUNT(*) as count FROM tokens WHERE token_date = CURDATE() AND status IN ('Waiting', 'Called')")
        stats['active_tokens'] = cursor.fetchone()['count']
        
        # Pending lab reports
        cursor.execute("SELECT COUNT(*) as count FROM lab_reports WHERE status != 'Completed'")
        stats['pending_reports'] = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
    
    return jsonify(stats)

# ==================== PATIENT MANAGEMENT ====================

@app.route('/patients')
@login_required
@role_required(['Chairman', 'Manager', 'Admin', 'Reception', 'Doctor'])
def patients():
    return render_template('patients.html')

@app.route('/api/patients', methods=['GET', 'POST'])
@login_required
def manage_patients():
    conn = get_db_connection()
    
    if request.method == 'GET':
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM patients ORDER BY registration_date DESC")
            patients = cursor.fetchall()
            cursor.close()
            conn.close()
            
            # Convert date objects to strings
            for patient in patients:
                patient['date_of_birth'] = patient['date_of_birth'].strftime('%Y-%m-%d')
                patient['registration_date'] = patient['registration_date'].strftime('%Y-%m-%d %H:%M:%S')
            
            return jsonify(patients)
        return jsonify([])
    
    elif request.method == 'POST':
        data = request.json
        
        if conn:
            cursor = conn.cursor()
            
            # Generate unique patient ID
            cursor.execute("SELECT patient_id FROM patients ORDER BY patient_id DESC LIMIT 1")
            last_id = cursor.fetchone()
            
            if last_id:
                num = int(last_id[0][3:]) + 1
                patient_id = f"PAT{num:03d}"
            else:
                patient_id = "PAT001"
            
            # Insert patient
            query = """INSERT INTO patients 
                        (patient_id, first_name, last_name, date_of_birth, gender, phone, email, address, blood_group, emergency_contact)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            
            values = (patient_id, data['first_name'], data['last_name'], data['date_of_birth'],
                        data['gender'], data['phone'], data.get('email'), data.get('address'),
                        data.get('blood_group'), data.get('emergency_contact'))
            
            cursor.execute(query, values)
            conn.commit()
            
            # Create patient login
            username = f"patient_{patient_id.lower()}"
            password = data['phone'][-6:]  # Last 6 digits of phone
            
            user_query = """INSERT INTO users (username, password, role, full_name, email, phone, patient_id)
                            VALUES (%s, %s, 'Patient', %s, %s, %s, %s)"""
            user_values = (username, password, f"{data['first_name']} {data['last_name']}", 
                            data.get('email'), data['phone'], patient_id)
            
            cursor.execute(user_query, user_values)
            conn.commit()
            
            cursor.close()
            conn.close()
            
            return jsonify({'success': True, 'patient_id': patient_id, 'username': username, 'password': password})
        
        return jsonify({'success': False, 'message': 'Database error'})

# ==================== APPOINTMENTS ====================

@app.route('/appointments')
@login_required
def appointments():
    return render_template('appointments.html')

@app.route('/api/appointments', methods=['GET', 'POST'])
@login_required
def manage_appointments():
    conn = get_db_connection()
    
    if request.method == 'GET':
        if conn:
            cursor = conn.cursor(dictionary=True)
            query = """SELECT a.*, p.first_name, p.last_name, u.full_name as doctor_name
                      FROM appointments a
                      JOIN patients p ON a.patient_id = p.patient_id
                      JOIN users u ON a.doctor_id = u.user_id
                      ORDER BY a.appointment_date DESC, a.appointment_time DESC"""
            cursor.execute(query)
            appointments = cursor.fetchall()
            cursor.close()
            conn.close()
            
            for apt in appointments:
                apt['appointment_date'] = apt['appointment_date'].strftime('%Y-%m-%d')
                apt['appointment_time'] = str(apt['appointment_time'])
                apt['created_at'] = apt['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            
            return jsonify(appointments)
        return jsonify([])
    
    elif request.method == 'POST':
        data = request.json
        
        if conn:
            cursor = conn.cursor()
            query = """INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, reason, status)
                      VALUES (%s, %s, %s, %s, %s, 'Scheduled')"""
            values = (data['patient_id'], data['doctor_id'], data['appointment_date'], 
                     data['appointment_time'], data.get('reason', ''))
            
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({'success': True})
        
        return jsonify({'success': False})

# ==================== OPD TOKEN SYSTEM ====================

@app.route('/tokens')
@login_required
def tokens():
    return render_template('tokens.html')

@app.route('/api/tokens', methods=['GET', 'POST'])
@login_required
def manage_tokens():
    conn = get_db_connection()
    
    if request.method == 'GET':
        if conn:
            cursor = conn.cursor(dictionary=True)
            query = """SELECT t.*, p.first_name, p.last_name, u.full_name as doctor_name
                      FROM tokens t
                      JOIN patients p ON t.patient_id = p.patient_id
                      JOIN users u ON t.doctor_id = u.user_id
                      WHERE t.token_date = CURDATE()
                      ORDER BY t.token_number ASC"""
            cursor.execute(query)
            tokens = cursor.fetchall()
            cursor.close()
            conn.close()
            
            for token in tokens:
                token['token_date'] = token['token_date'].strftime('%Y-%m-%d')
                token['created_at'] = token['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                if token['called_at']:
                    token['called_at'] = token['called_at'].strftime('%Y-%m-%d %H:%M:%S')
                if token['completed_at']:
                    token['completed_at'] = token['completed_at'].strftime('%Y-%m-%d %H:%M:%S')
            
            return jsonify(tokens)
        return jsonify([])
    
    elif request.method == 'POST':
        data = request.json
        
        if conn:
            cursor = conn.cursor()
            
            # Get next token number
            cursor.execute("SELECT MAX(token_number) as max_token FROM tokens WHERE token_date = CURDATE() AND doctor_id = %s", 
                          (data['doctor_id'],))
            result = cursor.fetchone()
            next_token = (result[0] or 0) + 1
            
            query = """INSERT INTO tokens (token_number, patient_id, doctor_id, token_date, status)
                      VALUES (%s, %s, %s, CURDATE(), 'Waiting')"""
            cursor.execute(query, (next_token, data['patient_id'], data['doctor_id']))
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({'success': True, 'token_number': next_token})
        
        return jsonify({'success': False})

@app.route('/api/tokens/<int:token_id>/call', methods=['PUT'])
@login_required
@role_required(['Doctor', 'Reception'])
def call_token(token_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE tokens SET status = 'Called', called_at = NOW() WHERE token_id = %s", (token_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/token-display')
def token_display():
    return render_template('token_display.html')

# ==================== DOCTOR & PRESCRIPTIONS ====================

@app.route('/prescriptions')
@login_required
@role_required(['Doctor'])
def prescriptions():
    return render_template('prescriptions.html')

@app.route('/api/prescriptions', methods=['GET', 'POST'])
@login_required
def manage_prescriptions():
    conn = get_db_connection()
    
    if request.method == 'GET':
        patient_id = request.args.get('patient_id')
        
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            if patient_id:
                query = """SELECT pr.*, p.first_name, p.last_name, u.full_name as doctor_name
                          FROM prescriptions pr
                          JOIN patients p ON pr.patient_id = p.patient_id
                          JOIN users u ON pr.doctor_id = u.user_id
                          WHERE pr.patient_id = %s
                          ORDER BY pr.prescription_date DESC"""
                cursor.execute(query, (patient_id,))
            else:
                query = """SELECT pr.*, p.first_name, p.last_name, u.full_name as doctor_name
                          FROM prescriptions pr
                          JOIN patients p ON pr.patient_id = p.patient_id
                          JOIN users u ON pr.doctor_id = u.user_id
                          ORDER BY pr.prescription_date DESC"""
                cursor.execute(query)
            
            prescriptions = cursor.fetchall()
            cursor.close()
            conn.close()
            
            for pres in prescriptions:
                pres['prescription_date'] = pres['prescription_date'].strftime('%Y-%m-%d')
                pres['created_at'] = pres['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                pres['medicines'] = json.loads(pres['medicines'])
            
            return jsonify(prescriptions)
        return jsonify([])
    
    elif request.method == 'POST':
        data = request.json
        
        if conn:
            cursor = conn.cursor()
            medicines_json = json.dumps(data['medicines'])
            
            query = """INSERT INTO prescriptions (patient_id, doctor_id, prescription_date, diagnosis, medicines, notes)
                      VALUES (%s, %s, CURDATE(), %s, %s, %s)"""
            values = (data['patient_id'], session['user_id'], data.get('diagnosis', ''), 
                     medicines_json, data.get('notes', ''))
            
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({'success': True})
        
        return jsonify({'success': False})
    


@app.route('/generate-captcha')
def generate_captcha():
    captcha = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    session['captcha'] = captcha
    return jsonify({'captcha': captcha})


# ==================== PHARMACY ====================

@app.route('/pharmacy')
@login_required
@role_required(['Pharmacist', 'Admin', 'Manager'])
def pharmacy():
    return render_template('pharmacy.html')

@app.route('/api/pharmacy/inventory', methods=['GET', 'POST'])
@login_required
def pharmacy_inventory():
    conn = get_db_connection()
    
    if request.method == 'GET':
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM pharmacy_inventory ORDER BY medicine_name")
            inventory = cursor.fetchall()
            cursor.close()
            conn.close()
            
            for item in inventory:
                if item['expiry_date']:
                    item['expiry_date'] = item['expiry_date'].strftime('%Y-%m-%d')
                item['created_at'] = item['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                item['updated_at'] = item['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
            
            return jsonify(inventory)
        return jsonify([])
    
    elif request.method == 'POST':
        data = request.json
        
        if conn:
            cursor = conn.cursor()
            query = """INSERT INTO pharmacy_inventory 
                      (medicine_name, category, manufacturer, price, stock_quantity, reorder_level, expiry_date)
                      VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            values = (data['medicine_name'], data.get('category'), data.get('manufacturer'),
                     data['price'], data['stock_quantity'], data.get('reorder_level', 10),
                     data.get('expiry_date'))
            
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({'success': True})
        
        return jsonify({'success': False})

@app.route('/api/pharmacy/sales', methods=['POST'])
@login_required
@role_required(['Pharmacist'])
def pharmacy_sales():
    data = request.json
    conn = get_db_connection()
    
    if conn:
        cursor = conn.cursor()
        
        # Create sale record
        items_json = json.dumps(data['items'])
        query = """INSERT INTO pharmacy_sales 
                  (patient_id, prescription_id, sale_date, items, total_amount, payment_method, status)
                  VALUES (%s, %s, CURDATE(), %s, %s, %s, 'Paid')"""
        values = (data['patient_id'], data.get('prescription_id'), items_json, 
                 data['total_amount'], data.get('payment_method', 'Cash'))
        
        cursor.execute(query, values)
        
        # Update inventory
        for item in data['items']:
            cursor.execute("UPDATE pharmacy_inventory SET stock_quantity = stock_quantity - %s WHERE medicine_id = %s",
                          (item['quantity'], item['medicine_id']))
        
        # Create billing entry
        cursor.execute("""INSERT INTO billing (patient_id, bill_type, bill_date, amount, payment_status, payment_method)
                         VALUES (%s, 'Pharmacy', CURDATE(), %s, 'Paid', %s)""",
                      (data['patient_id'], data['total_amount'], data.get('payment_method', 'Cash')))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True})
    
    return jsonify({'success': False})

# ==================== LABORATORY ====================

@app.route('/laboratory')
@login_required
@role_required(['Lab Staff', 'Doctor', 'Admin'])
def laboratory():
    return render_template('laboratory.html')

@app.route('/api/lab/tests', methods=['GET'])
@login_required
def lab_tests():
    conn = get_db_connection()
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM lab_tests WHERE status = 'Active' ORDER BY test_name")
        tests = cursor.fetchall()
        cursor.close()
        conn.close()
        
        for test in tests:
            test['created_at'] = test['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify(tests)
    return jsonify([])

@app.route('/api/lab/reports', methods=['GET', 'POST'])
@login_required
def lab_reports():
    conn = get_db_connection()
    
    if request.method == 'GET':
        if conn:
            cursor = conn.cursor(dictionary=True)
            query = """SELECT lr.*, p.first_name, p.last_name, lt.test_name, u.full_name as doctor_name
                      FROM lab_reports lr
                      JOIN patients p ON lr.patient_id = p.patient_id
                      JOIN lab_tests lt ON lr.test_id = lt.test_id
                      JOIN users u ON lr.doctor_id = u.user_id
                      ORDER BY lr.test_date DESC"""
            cursor.execute(query)
            reports = cursor.fetchall()
            cursor.close()
            conn.close()
            
            for report in reports:
                report['test_date'] = report['test_date'].strftime('%Y-%m-%d')
                report['created_at'] = report['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                if report['completed_at']:
                    report['completed_at'] = report['completed_at'].strftime('%Y-%m-%d %H:%M:%S')
            
            return jsonify(reports)
        return jsonify([])
    
    elif request.method == 'POST':
        data = request.json
        
        if conn:
            cursor = conn.cursor()
            query = """INSERT INTO lab_reports (patient_id, doctor_id, test_id, test_date, status)
                      VALUES (%s, %s, %s, CURDATE(), 'Requested')"""
            cursor.execute(query, (data['patient_id'], data['doctor_id'], data['test_id']))
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({'success': True})
        
        return jsonify({'success': False})

# ==================== BILLING ====================

@app.route('/billing')
@login_required
def billing():
    return render_template('billing.html')

@app.route('/api/billing/<patient_id>')
@login_required
def get_patient_bills(patient_id):
    conn = get_db_connection()
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM billing WHERE patient_id = %s ORDER BY bill_date DESC", (patient_id,))
        bills = cursor.fetchall()
        cursor.close()
        conn.close()
        
        for bill in bills:
            bill['bill_date'] = bill['bill_date'].strftime('%Y-%m-%d')
            bill['created_at'] = bill['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify(bills)
    return jsonify([])

# ==================== PATIENT PORTAL ====================

@app.route('/patient-portal')
@login_required
@role_required(['Patient'])
def patient_portal():
    return render_template('patient_portal.html')

@app.route('/api/patient/info')
@login_required
@role_required(['Patient'])
def patient_info():
    patient_id = session.get('patient_id')
    conn = get_db_connection()
    
    if conn and patient_id:
        cursor = conn.cursor(dictionary=True)
        
        # Get patient details
        cursor.execute("SELECT * FROM patients WHERE patient_id = %s", (patient_id,))
        patient = cursor.fetchone()
        
        # Get appointments
        cursor.execute("""SELECT a.*, u.full_name as doctor_name 
                         FROM appointments a 
                         JOIN users u ON a.doctor_id = u.user_id
                         WHERE a.patient_id = %s 
                         ORDER BY a.appointment_date DESC LIMIT 5""", (patient_id,))
        appointments = cursor.fetchall()
        
        # Get prescriptions
        cursor.execute("""SELECT pr.*, u.full_name as doctor_name 
                         FROM prescriptions pr 
                         JOIN users u ON pr.doctor_id = u.user_id
                         WHERE pr.patient_id = %s 
                         ORDER BY pr.prescription_date DESC LIMIT 5""", (patient_id,))
        prescriptions = cursor.fetchall()
        
        # Get lab reports
        cursor.execute("""SELECT lr.*, lt.test_name 
                         FROM lab_reports lr 
                         JOIN lab_tests lt ON lr.test_id = lt.test_id
                         WHERE lr.patient_id = %s 
                         ORDER BY lr.test_date DESC LIMIT 5""", (patient_id,))
        reports = cursor.fetchall()
        
        # Get bills
        cursor.execute("SELECT * FROM billing WHERE patient_id = %s ORDER BY bill_date DESC LIMIT 5", (patient_id,))
        bills = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Format dates
        if patient:
            patient['date_of_birth'] = patient['date_of_birth'].strftime('%Y-%m-%d')
        
        return jsonify({
            'patient': patient,
            'appointments': appointments,
            'prescriptions': prescriptions,
            'reports': reports,
            'bills': bills
        })
    
    return jsonify({'error': 'Patient not found'}), 404

# ==================== AI CHATBOT API ====================

@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    phone = data.get('phone')
    query = data.get('query', '').lower()
    
    conn = get_db_connection()
    response_text = "Sorry, I didn't understand your query. Please try: 'my token', 'my appointment', or 'my bill'"
    query_type = 'unknown'
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        # Find patient by phone
        cursor.execute("SELECT patient_id, first_name FROM patients WHERE phone = %s", (phone,))
        patient = cursor.fetchone()
        
        if patient:
            patient_id = patient['patient_id']
            
            if 'token' in query:
                # Get today's token
                cursor.execute("""SELECT token_number, status 
                                 FROM tokens 
                                 WHERE patient_id = %s AND token_date = CURDATE()
                                 ORDER BY created_at DESC LIMIT 1""", (patient_id,))
                token = cursor.fetchone()
                
                if token:
                    response_text = f"Hello {patient['first_name']}! Your token number is {token['token_number']}. Status: {token['status']}"
                    query_type = 'token'
                else:
                    response_text = f"Hello {patient['first_name']}! You don't have a token for today."
                    query_type = 'token'
            
            elif 'appointment' in query:
                # Get upcoming appointment
                cursor.execute("""SELECT appointment_date, appointment_time 
                                 FROM appointments 
                                 WHERE patient_id = %s AND appointment_date >= CURDATE() AND status = 'Scheduled'
                                 ORDER BY appointment_date ASC LIMIT 1""", (patient_id,))
                appointment = cursor.fetchone()
                
                if appointment:
                    apt_date = appointment['appointment_date'].strftime('%Y-%m-%d')
                    apt_time = str(appointment['appointment_time'])
                    response_text = f"Hello {patient['first_name']}! Your next appointment is on {apt_date} at {apt_time}."
                    query_type = 'appointment'
                else:
                    response_text = f"Hello {patient['first_name']}! You don't have any upcoming appointments."
                    query_type = 'appointment'
            
            elif 'bill' in query:
                # Get recent bill
                cursor.execute("""SELECT bill_type, amount, payment_status 
                                 FROM billing 
                                 WHERE patient_id = %s 
                                 ORDER BY bill_date DESC LIMIT 1""", (patient_id,))
                bill = cursor.fetchone()
                
                if bill:
                    response_text = f"Hello {patient['first_name']}! Your last {bill['bill_type']} bill was ₹{bill['amount']}. Status: {bill['payment_status']}"
                    query_type = 'bill'
                else:
                    response_text = f"Hello {patient['first_name']}! You don't have any bills yet."
                    query_type = 'bill'
        else:
            response_text = "Patient not found. Please register at the hospital first."
        
        # Log the chat
        cursor.execute("""INSERT INTO ai_chat_logs (patient_id, phone_number, query, response, query_type)
                         VALUES (%s, %s, %s, %s, %s)""",
                      (patient['patient_id'] if patient else None, phone, query, response_text, query_type))
        conn.commit()
        cursor.close()
        conn.close()
    
    return jsonify({'response': response_text})

# ==================== DOCTORS LIST ====================

@app.route('/api/doctors')
@login_required
def get_doctors():
    conn = get_db_connection()
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT user_id, full_name, specialization FROM users WHERE role = 'Doctor' AND status = 'Active'")
        doctors = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(doctors)
    
    return jsonify([])

# ==================== RUN APPLICATION ====================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)