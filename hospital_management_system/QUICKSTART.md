# 🚀 Quick Start Guide - Smart Hospital Management System

## For Alexander Saji Varghese

This guide will help you get the system running in **15 minutes**!

---

## ⚡ Step-by-Step Installation

### Step 1: Install MySQL (5 minutes)

**Ubuntu/Linux:**
```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql
```

**Windows:**
1. Download MySQL Installer from: https://dev.mysql.com/downloads/installer/
2. Run installer and choose "Developer Default"
3. Set root password (remember this!)
4. Complete installation

**macOS:**
```bash
brew install mysql
brew services start mysql
```

### Step 2: Create Database (2 minutes)

Open terminal/command prompt and run:

```bash
# Login to MySQL
mysql -u root -p
# Enter your MySQL password when prompted
```

Inside MySQL, run these commands:

```sql
-- Create the database
CREATE DATABASE hospital_db;

-- Exit MySQL
EXIT;
```

Now import the schema:

```bash
# Navigate to project folder
cd hospital_management_system

# Import database schema
mysql -u root -p hospital_db < database/schema.sql
# Enter password when prompted
```

### Step 3: Install Python Dependencies (2 minutes)

```bash
# Make sure you're in the project folder
cd hospital_management_system

# Install required packages
pip install -r requirements.txt
```

If `pip` is not found, try:
```bash
pip3 install -r requirements.txt
```

### Step 4: Configure Database Connection (1 minute)

Open `app.py` in a text editor and find this section (around line 16):

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'YOUR_MYSQL_PASSWORD',  # Change this line
    'database': 'hospital_db'
}
```

Replace `YOUR_MYSQL_PASSWORD` with your actual MySQL root password.

Save the file.

### Step 5: Run the Application (1 minute)

```bash
python app.py
```

If that doesn't work, try:
```bash
python3 app.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
```

### Step 6: Access the System

Open your web browser and go to:
```
http://localhost:5000
```

---

## 🔐 Demo Accounts

Try logging in with these accounts:

### For Testing Full System (Use this first):
- **Username:** `chairman`
- **Password:** `chairman123`
- **Access:** Everything

### For Doctor Functions:
- **Username:** `dr_cardio`
- **Password:** `doctor123`
- **Access:** Appointments, Prescriptions, Lab Tests

### For Pharmacy:
- **Username:** `pharmacist`
- **Password:** `pharma123`
- **Access:** Inventory, Medicine Sales

### For Reception:
- **Username:** `reception`
- **Password:** `reception123`
- **Access:** Patient Registration, Appointments, Tokens

### For Patient View:
- **Username:** `patient1`
- **Password:** `patient123`
- **Access:** Personal portal with appointments, prescriptions, reports

---

## 🎯 Quick Testing Workflow

### Test 1: Register a New Patient
1. Login as `reception`
2. Go to "Patients"
3. Click "+ Add New Patient"
4. Fill the form and submit
5. Note the Patient ID (e.g., PAT004)

### Test 2: Generate a Token
1. Stay logged in as reception
2. Go to "Tokens"
3. Click "+ Generate New Token"
4. Enter the Patient ID you just created
5. Select a doctor
6. Submit

### Test 3: View Token Display
1. Open a new browser tab
2. Go to: `http://localhost:5000/token-display`
3. Press F11 for fullscreen
4. Watch the token appear!

### Test 4: Create Prescription (Login as Doctor)
1. Logout and login as `dr_cardio`
2. Go to "Prescriptions"
3. Write a prescription for your test patient
4. Add medicines with dosage and frequency

### Test 5: Dispense Medicine (Login as Pharmacist)
1. Logout and login as `pharmacist`
2. Go to "Pharmacy"
3. Click "Sales" tab
4. Create a sale for your patient
5. Add prescribed medicines

---

## 🛠️ Troubleshooting

### Problem: "Database connection error"
**Solution:** Check if MySQL is running:
```bash
# Linux/Mac
sudo systemctl status mysql

# Windows - Open Services and check MySQL80 service
```

### Problem: "Port 5000 already in use"
**Solution:** Either:
1. Stop the other application using port 5000, OR
2. Change port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Use 5001 instead
```

### Problem: "Module not found"
**Solution:** Reinstall dependencies:
```bash
pip install --upgrade flask mysql-connector-python
```

### Problem: "Access denied for user 'root'"
**Solution:** Your MySQL password is wrong. Reset it:
```bash
# Linux/Mac
sudo mysql
ALTER USER 'root'@'localhost' IDENTIFIED BY 'newpassword';
FLUSH PRIVILEGES;
EXIT;

# Update app.py with the new password
```

---

## 📱 Features to Try

### 1. Token Display on TV
- Open `/token-display` on a large screen
- Press F11 for fullscreen mode
- It auto-refreshes every 3 seconds

### 2. Patient Portal
- Login as `patient1`
- View your appointments
- Check prescriptions
- Download lab reports

### 3. Real-time Updates
- Open Tokens page in one browser
- Open Token Display in another
- Call a token and watch both update!

### 4. Pharmacy Inventory
- Login as pharmacist
- Add new medicines
- Check stock levels
- Create sales

---

## 🎓 Learning Tips for Alexander

1. **Understand the Flow:**
   - Patient Registration → Token Generation → Doctor Consultation → Prescription → Pharmacy Sale

2. **Explore the Database:**
   ```bash
   mysql -u root -p hospital_db
   SHOW TABLES;
   SELECT * FROM patients;
   SELECT * FROM tokens WHERE token_date = CURDATE();
   ```

3. **Check API Responses:**
   - Open browser Developer Tools (F12)
   - Go to Network tab
   - Click around the app
   - See all API calls and responses

4. **Modify and Experiment:**
   - Change colors in CSS
   - Add new fields to forms
   - Create new dashboard statistics
   - Add email notifications

---

## 📊 Next Steps

### Beginner Level:
- Add more patient fields (insurance, occupation)
- Create appointment reminders
- Add search filters for inventory

### Intermediate Level:
- Implement email notifications using SMTP
- Add data export to Excel
- Create analytics dashboard with charts
- Implement appointment cancellation

### Advanced Level:
- Integrate WhatsApp bot using Twilio API
- Add PDF report generation
- Implement real SMS notifications
- Create mobile-responsive design
- Add appointment calendar view

---

## 💡 Pro Tips

1. **Always backup your database:**
   ```bash
   mysqldump -u root -p hospital_db > backup.sql
   ```

2. **Test with different roles:**
   - Each role sees different menus
   - This is called Role-Based Access Control (RBAC)

3. **Watch the console:**
   - Keep terminal open while running
   - You'll see all API calls and errors

4. **Use incognito mode:**
   - For testing different user logins simultaneously
   - Regular window for doctor, incognito for pharmacist

---

## ✅ Success Checklist

- [ ] MySQL installed and running
- [ ] Database created and schema imported
- [ ] Python dependencies installed
- [ ] app.py configured with correct password
- [ ] Application running on port 5000
- [ ] Can access login page
- [ ] Successfully logged in as chairman
- [ ] Registered a test patient
- [ ] Generated a token
- [ ] Viewed token display

---

## 🎉 You're Ready!

If you've completed all steps, you now have a fully functional Hospital Management System running on your computer!

**Need Help?**
- Check README.md for detailed documentation
- Review the database schema in `database/schema.sql`
- Examine the code in `app.py` to understand the backend
- Inspect HTML templates to see frontend structure

**Good Luck with Your Data Science Journey!**

---

**Created for:** Alexander Saji Varghese  
**Project:** Smart Hospital Management System  
**Date:** February 2026
