-- Smart Hospital Management System Database Schema
-- Created for Alexander Saji Varghese

-- Drop existing tables if they exist
DROP TABLE IF EXISTS ai_chat_logs;
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS billing;
DROP TABLE IF EXISTS lab_reports;
DROP TABLE IF EXISTS lab_tests;
DROP TABLE IF EXISTS pharmacy_sales;
DROP TABLE IF EXISTS prescriptions;
DROP TABLE IF EXISTS tokens;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS pharmacy_inventory;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS patients;

-- Patients Table
CREATE TABLE patients (
    patient_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    phone VARCHAR(15) NOT NULL UNIQUE,
    email VARCHAR(100),
    address TEXT,
    blood_group VARCHAR(5),
    emergency_contact VARCHAR(15),
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Active', 'Inactive') DEFAULT 'Active'
);

-- Users Table (Staff, Doctors, etc.)
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('Chairman', 'Manager', 'Admin', 'Doctor', 'Lab Staff', 'Pharmacist', 'Reception', 'Patient') NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(15),
    specialization VARCHAR(100), -- For doctors
    patient_id VARCHAR(20), -- Link to patient if role is Patient
    status ENUM('Active', 'Inactive') DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE SET NULL
);

-- Appointments Table
CREATE TABLE appointments (
    appointment_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id VARCHAR(20) NOT NULL,
    doctor_id INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    reason TEXT,
    status ENUM('Scheduled', 'Completed', 'Cancelled', 'No Show') DEFAULT 'Scheduled',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- OPD Token System
CREATE TABLE tokens (
    token_id INT AUTO_INCREMENT PRIMARY KEY,
    token_number INT NOT NULL,
    patient_id VARCHAR(20) NOT NULL,
    doctor_id INT NOT NULL,
    token_date DATE NOT NULL,
    status ENUM('Waiting', 'Called', 'Completed', 'Cancelled') DEFAULT 'Waiting',
    called_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Prescriptions Table
CREATE TABLE prescriptions (
    prescription_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id VARCHAR(20) NOT NULL,
    doctor_id INT NOT NULL,
    appointment_id INT,
    prescription_date DATE NOT NULL,
    diagnosis TEXT,
    medicines TEXT NOT NULL, -- JSON format: [{name, dosage, frequency, duration}]
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id) ON DELETE SET NULL
);

-- Pharmacy Inventory
CREATE TABLE pharmacy_inventory (
    medicine_id INT AUTO_INCREMENT PRIMARY KEY,
    medicine_name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50),
    manufacturer VARCHAR(100),
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    reorder_level INT DEFAULT 10,
    expiry_date DATE,
    status ENUM('Available', 'Out of Stock', 'Expired') DEFAULT 'Available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Pharmacy Sales
CREATE TABLE pharmacy_sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id VARCHAR(20) NOT NULL,
    prescription_id INT,
    sale_date DATE NOT NULL,
    items TEXT NOT NULL, -- JSON format: [{medicine_id, medicine_name, quantity, price}]
    total_amount DECIMAL(10, 2) NOT NULL,
    payment_method ENUM('Cash', 'Card', 'UPI', 'Insurance') DEFAULT 'Cash',
    status ENUM('Paid', 'Pending') DEFAULT 'Paid',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (prescription_id) REFERENCES prescriptions(prescription_id) ON DELETE SET NULL
);

-- Lab Tests
CREATE TABLE lab_tests (
    test_id INT AUTO_INCREMENT PRIMARY KEY,
    test_name VARCHAR(100) NOT NULL,
    test_category VARCHAR(50),
    price DECIMAL(10, 2) NOT NULL,
    description TEXT,
    normal_range TEXT,
    status ENUM('Active', 'Inactive') DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Lab Reports
CREATE TABLE lab_reports (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id VARCHAR(20) NOT NULL,
    doctor_id INT NOT NULL,
    test_id INT NOT NULL,
    test_date DATE NOT NULL,
    result_value VARCHAR(100),
    result_file VARCHAR(255), -- Path to uploaded PDF
    status ENUM('Requested', 'In Progress', 'Completed') DEFAULT 'Requested',
    remarks TEXT,
    uploaded_by INT, -- Lab staff user_id
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (test_id) REFERENCES lab_tests(test_id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES users(user_id) ON DELETE SET NULL
);

-- Billing Table
CREATE TABLE billing (
    bill_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id VARCHAR(20) NOT NULL,
    bill_type ENUM('Pharmacy', 'Lab', 'Consultation', 'Other') NOT NULL,
    bill_date DATE NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_status ENUM('Paid', 'Pending', 'Partial') DEFAULT 'Pending',
    payment_method ENUM('Cash', 'Card', 'UPI', 'Insurance'),
    reference_id INT, -- Links to pharmacy_sales, lab_reports, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);

-- Notifications Table
CREATE TABLE notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id VARCHAR(20) NOT NULL,
    notification_type ENUM('Email', 'WhatsApp', 'SMS') NOT NULL,
    subject VARCHAR(255),
    message TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Sent', 'Failed', 'Pending') DEFAULT 'Sent',
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);

-- AI Chat Logs
CREATE TABLE ai_chat_logs (
    chat_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id VARCHAR(20),
    phone_number VARCHAR(15) NOT NULL,
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    query_type VARCHAR(50), -- 'token', 'appointment', 'bill', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE SET NULL
);

-- Insert Sample Data

-- Insert sample patients
INSERT INTO patients (patient_id, first_name, last_name, date_of_birth, gender, phone, email, address, blood_group, emergency_contact) VALUES
('PAT001', 'Rajesh', 'Kumar', '1985-05-15', 'Male', '9876543210', 'rajesh.kumar@email.com', '123 MG Road, Kollam', 'O+', '9876543211'),
('PAT002', 'Priya', 'Sharma', '1990-08-22', 'Female', '9876543212', 'priya.sharma@email.com', '456 Beach Road, Kollam', 'A+', '9876543213'),
('PAT003', 'Anand', 'Nair', '1978-12-10', 'Male', '9876543214', 'anand.nair@email.com', '789 Temple Street, Kollam', 'B+', '9876543215');

-- Insert sample users (staff and doctors)
INSERT INTO users (username, password, role, full_name, email, phone, specialization, patient_id) VALUES
('chairman', 'chairman123', 'Chairman', 'Dr. Suresh Menon', 'chairman@hospital.com', '9800000001', NULL, NULL),
('manager', 'manager123', 'Manager', 'Anil Kumar', 'manager@hospital.com', '9800000002', NULL, NULL),
('admin', 'admin123', 'Admin', 'Sneha Pillai', 'admin@hospital.com', '9800000003', NULL, NULL),
('dr_cardio', 'doctor123', 'Doctor', 'Dr. Ramesh Babu', 'ramesh@hospital.com', '9800000004', 'Cardiology', NULL),
('dr_ortho', 'doctor123', 'Doctor', 'Dr. Lakshmi Menon', 'lakshmi@hospital.com', '9800000005', 'Orthopedics', NULL),
('labstaff', 'lab123', 'Lab Staff', 'Vinod Thomas', 'lab@hospital.com', '9800000006', NULL, NULL),
('pharmacist', 'pharma123', 'Pharmacist', 'Maya Krishnan', 'pharmacy@hospital.com', '9800000007', NULL, NULL),
('reception', 'reception123', 'Reception', 'Asha Menon', 'reception@hospital.com', '9800000008', NULL, NULL),
('patient1', 'patient123', 'Patient', 'Rajesh Kumar', 'rajesh.kumar@email.com', '9876543210', NULL, 'PAT001');

-- Insert sample pharmacy inventory
INSERT INTO pharmacy_inventory (medicine_name, category, manufacturer, price, stock_quantity, reorder_level, expiry_date) VALUES
('Paracetamol 500mg', 'Analgesic', 'PharmaCo', 5.00, 500, 50, '2026-12-31'),
('Amoxicillin 250mg', 'Antibiotic', 'MediPharma', 15.00, 300, 30, '2026-06-30'),
('Cetirizine 10mg', 'Antihistamine', 'AllergyFree', 8.00, 200, 20, '2026-09-30'),
('Metformin 500mg', 'Antidiabetic', 'DiabetesCare', 12.00, 400, 40, '2027-03-31'),
('Omeprazole 20mg', 'Antacid', 'GastroPharma', 10.00, 250, 25, '2026-11-30');

-- Insert sample lab tests
INSERT INTO lab_tests (test_name, test_category, price, description, normal_range) VALUES
('Complete Blood Count (CBC)', 'Hematology', 350.00, 'Complete blood count analysis', 'WBC: 4000-11000, RBC: 4.5-6.0'),
('Blood Sugar (Fasting)', 'Biochemistry', 150.00, 'Fasting blood glucose test', '70-100 mg/dL'),
('Lipid Profile', 'Biochemistry', 500.00, 'Cholesterol and lipid analysis', 'Total Cholesterol < 200 mg/dL'),
('Liver Function Test (LFT)', 'Biochemistry', 600.00, 'Liver enzyme analysis', 'ALT: 7-56 U/L, AST: 10-40 U/L'),
('Kidney Function Test (KFT)', 'Biochemistry', 550.00, 'Kidney function markers', 'Creatinine: 0.6-1.2 mg/dL');
