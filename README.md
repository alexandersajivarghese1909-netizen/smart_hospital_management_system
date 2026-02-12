# 🏥 Smart Hospital Management System

**Developer:** Alexander Saji Varghese  
**Technology Stack:** Python (Flask), MySQL, HTML/CSS/JavaScript  
**Project Type:** Full-Stack Web Application

---
## 🚧 Project Status

This project is currently a **partially developed system** and is under active development.

While many core hospital management features are already implemented, several advanced modules and optimizations are planned for future versions. This project is intended to grow over time as I continue learning, experimenting, and improving my skills in full-stack development and data science.

🚀 I will continue enhancing this system with better UI/UX, stronger security, more automation, and AI-driven features in future updates.


## 📋 Project Overview

The Smart Hospital Management System is a comprehensive digital solution for modern hospitals that integrates patient care, administration, and communication into one secure, efficient platform. It automates all major hospital operations including patient registration, appointments, OPD tokens, doctor prescriptions, pharmacy management, laboratory, billing, and includes an AI-powered WhatsApp chatbot.

---

## ✨ Key Features

### 1. **Patient Management**
- Auto-generated unique Patient IDs (PAT001, PAT002, etc.)
- Complete patient records with demographics and medical history
- Patient portal for viewing appointments, prescriptions, and reports

### 2. **Role-Based Access Control**
Supports 8 different user roles:
- Chairman (Full access)
- Manager
- Admin Staff
- Doctor
- Lab Staff
- Pharmacist
- Reception
- Patient

### 3. **Appointment System**
- Book appointments with specific doctors
- Calendar view for doctors
- Appointment status tracking (Scheduled, Completed, Cancelled, No Show)

### 4. **OPD Token Calling System**
- Auto-generated token numbers for each doctor
- Real-time token display on waiting area TV screen
- Token status: Waiting → Called → Completed

### 5. **Doctor & Prescription Module**
- Doctors can write digital prescriptions
- Prescriptions include: diagnosis, medicines, dosage, frequency, duration
- Prescriptions linked directly to pharmacy

### 6. **Pharmacy Management**
- Medicine inventory with stock tracking
- Prescription-controlled dispensing (only prescribed medicines can be billed)
- Automatic stock updates after sales
- Low stock alerts

### 7. **Laboratory Module**
- Doctors can request lab tests
- Lab staff upload test results
- Patients can view/download reports from portal

### 8. **Billing System**
- Comprehensive billing for pharmacy, lab tests, consultations
- Payment tracking (Paid, Pending, Partial)
- Patient-wise billing history

### 9. **AI WhatsApp Bot**
Patients can message:
- "My token" - Get current token status
- "My appointment" - View next appointment
- "My bill" - Check recent bills

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- MySQL Server 5.7 or higher
- pip (Python package manager)

### Step 1: Install MySQL

**For Ubuntu/Linux:**
```bash
sudo apt update
sudo apt install mysql-server
sudo mysql_secure_installation
```

**For Windows:**
Download and install from: https://dev.mysql.com/downloads/mysql/

**For macOS:**
```bash
brew install mysql
```

### Step 2: Create Database

1. Login to MySQL:
```bash
mysql -u root -p
```

2. Create database:
```sql
CREATE DATABASE hospital_db;
EXIT;
```

3. Import the schema:
```bash
mysql -u root -p hospital_db < database/schema.sql
```

### Step 3: Install Python Dependencies

```bash
cd hospital_management_system
pip install flask mysql-connector-python
```

### Step 4: Configure Database Connection

Edit `app.py` and update the database credentials:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'YOUR_MYSQL_PASSWORD',  # Change this
    'database': 'hospital_db'
}
```

### Step 5: Run the Application

```bash
python app.py
```

The application will start on: `http://localhost:5000`

---

## 🔐 Demo Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Chairman | chairman | chairman123 |
| Manager | manager | manager123 |
| Doctor (Cardiology) | dr_cardio | doctor123 |
| Doctor (Orthopedics) | dr_ortho | doctor123 |
| Lab Staff | labstaff | lab123 |
| Pharmacist | pharmacist | pharma123 |
| Reception | reception | reception123 |
| Patient | patient1 | patient123 |

---

## 📱 Using the System

### For Reception Staff:
1. Register new patients
2. Generate OPD tokens
3. Book appointments
4. Process billing

### For Doctors:
1. View patient tokens
2. Write prescriptions
3. Request lab tests
4. View patient history

### For Pharmacists:
1. View prescriptions
2. Dispense medicines (only prescribed items)
3. Manage inventory
4. Process pharmacy sales

### For Lab Staff:
1. View test requests
2. Upload test results
3. Manage lab reports

### For Patients:
1. Login to patient portal
2. View appointments, prescriptions, lab reports
3. Check billing history
4. Use WhatsApp bot for quick queries

---

## 🖥️ Token Display System

For waiting area TV display, open this URL in full-screen browser:
```
http://localhost:5000/token-display
```

Press `F11` for full-screen mode. The display auto-refreshes every 3 seconds.

---

## 🤖 AI Chatbot Integration

### WhatsApp Bot Setup (Optional - Requires Twilio)

1. Create Twilio account: https://www.twilio.com/
2. Get WhatsApp sandbox number
3. Configure webhook to: `http://your-server.com/api/chatbot`

**How patients use it:**
- Message: "My token" → Gets current token status
- Message: "My appointment" → Gets next appointment details
- Message: "My bill" → Gets recent bill information

---

## 📊 Database Schema

The system uses 13 main tables:

1. **patients** - Patient records
2. **users** - Staff and doctor accounts
3. **appointments** - Appointment scheduling
4. **tokens** - OPD token system
5. **prescriptions** - Doctor prescriptions
6. **pharmacy_inventory** - Medicine stock
7. **pharmacy_sales** - Pharmacy transactions
8. **lab_tests** - Available lab tests
9. **lab_reports** - Test results
10. **billing** - All billing records
11. **notifications** - Email/WhatsApp logs
12. **ai_chat_logs** - Chatbot conversation history

---

## 🔧 Troubleshooting

### Database Connection Error
- Check MySQL is running: `sudo service mysql status`
- Verify credentials in `app.py`
- Ensure database exists: `SHOW DATABASES;`

### Port Already in Use
Change port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change 5000 to 5001
```

### Prescription Not Showing in Pharmacy
- Ensure doctor has created the prescription
- Check patient_id is correct
- Verify prescription_id is linked

---

## 📈 Future Enhancements

- **Email Notifications**: Appointment reminders, bill alerts
- **SMS Integration**: Token notifications
- **Mobile App**: Native Android/iOS apps
- **Advanced Analytics**: Hospital performance dashboards
- **Telemedicine**: Video consultation integration
- **Insurance Integration**: Direct insurance claim processing
- **Multi-language Support**: Regional language support

---

## 🎓 Learning Outcomes (For Alexander)

This project covers:
- **Backend Development**: Flask framework, REST APIs
- **Database Design**: MySQL, relational database modeling
- **Frontend Development**: HTML, CSS, JavaScript
- **Authentication**: Session management, role-based access
- **Real-time Systems**: Token display, auto-refresh
- **Integration**: WhatsApp bot, email systems
- **Full-stack Architecture**: Complete CRUD operations

---

## 📞 Support

For issues or questions:
- Email: alexandersajivarghese1909@gmail.com
- GitHub: [text](https://github.com/alexandersajivarghese1909-netizen)

---

## 📄 License

This project is created for educational purposes as part of Alexander Saji Varghese's M.Tech Data Science program.

---

## 🙏 Acknowledgments

- Hospital management best practices
- Flask documentation
- MySQL community
- Open-source community

---

**© 2026 Alexander Saji Varghese | Smart Hospital Management System**
