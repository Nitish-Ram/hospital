from mysql.connector import connect, Error
from getpass import getpass
from datetime import datetime

try:
    conn = connect(
        host = 'localhost',
        user = 'root',
        password = 'test',
        database = 'hospital'
    )
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS staff (
                staff_id INT AUTO_INCREMENT PRIMARY KEY,
                staff_his_id INT, 
                cpr_no INT,
                staff_name VARCHAR(100),
                designation VARCHAR(100),
                department VARCHAR(100),
                user_name VARCHAR(100),
                passcode VARCHAR(100),
                access_level INT DEFAULT 1,
                dob DATE,
                email VARCHAR(100),
                phone_no VARCHAR(50),
                is_active ENUM('Yes','No') DEFAULT 'Yes',
                version INT DEFAULT 0,
                edited_by INT NULL,
                edited_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS patients (
                patient_id INT AUTO_INCREMENT PRIMARY KEY,
                patient_his_id INT,
                cpr_no INT,
                patient_name VARCHAR(100),
                dob DATE,
                email VARCHAR(100),
                phone_no VARCHAR(50),
                address VARCHAR(200),
                next_of_kin VARCHAR(100),
                relationship VARCHAR(50),
                emergency_contact VARCHAR(100),
                patient_status INT,
                FOREIGN KEY (patient_status) REFERENCES lookup_code(item_id),
                version INT DEFAULT 0,
                edited_by INT NULL,
                edited_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
                #patient_status ENUM('Active','Inactive','Deceased') DEFAULT 'Active'
except Error as e:
    print(e)

def create_staff(edited_by):
    while True:
        try:
            cpr_no = int(input("Enter staff's CPR number : "))
            break
        except ValueError:
            print("Enter only numbers.")
    staff_name = input("Enter name : ")
    designation = input("Enter designation : ")
    department = input("Enter department : ")
    user_name = input("Enter a username : ")
    passcode = getpass("Enter a password : ")
    while True:
        try:
            access_level = int(input("Enter access level : "))
            break
        except ValueError:
            print("Enter numbers only.")
    while True:
        passcode_retype = getpass("Retype the password : ")
        if passcode_retype == passcode:
            break
        else:
            print("Passwords do not match.")
    while True:
        try:
            dob_input = input("Enter date of birth (YYYY-MM-DD) : ")
            dob = datetime.strptime(dob_input, "%Y-%m-%d").date()
            break
        except ValueError:
            print("Invalid date format, use YYYY-MM-DD.")
    email = input("Enter email : ")
    phone_no = input("Enter phone number : ")
    sql = '''INSERT INTO staff (
                cpr_no, staff_name, designation, department, user_name, passcode, access_level, dob, email, phone_no, edited_by
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                '''
    cur.execute(sql, (cpr_no, staff_name, designation, department, user_name, passcode, access_level, dob, email, phone_no, edited_by))
    conn.commit()
    print("Staff member created successfully.")

def create_patient(edited_by):
    while True:
        try:
            cpr_no = int(input("Enter patient's CPR number : "))
            break
        except ValueError:
            print("Enter only numbers.")
    patient_name = input("Enter patient's name : ")
    while True:
        try:
            dob_input = ("Enter date of birth (YYYY-MM-DD) : ")
            dob = datetime.strptime(dob_input, "%Y-%m-%d").date()
            break
        except ValueError:
            print("Invalid date format, use YYYY-MM-DD")
    address = input("Enter patient's address : ")
    next_of_kin = input("Enter name of patient's 'Next-of'kin' : ")
    relationship = input(f"Enter patient's relationship with {next_of_kin} : ")
    emergency_contact = input("Enter patient's emergency contact : ")