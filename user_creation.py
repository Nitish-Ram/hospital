from mysql.connector import connect, Error
from getpass import getpass
from datetime import datetime
from tabulate import tabulate

try:
    conn = connect(
        host = 'mysql-guyandchair-hospitaldb344.l.aivencloud.com',
        port = '28557',
        user = 'avnadmin',
        password = 'AVNS_kHrKn7uSeIU17qOji3M',
        database = 'defaultdb',
        ssl_ca = 'certs/ca.pem'
    )
    
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS staff (
                staff_id INT AUTO_INCREMENT PRIMARY KEY,
                staff_his_id INT NULL, 
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
                patient_his_id INT NULL,
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
                is_active ENUM('Yes','No') DEFAULT 'Yes',
                FOREIGN KEY (patient_status) REFERENCES lookup_code(item_id),
                version INT DEFAULT 0,
                edited_by INT NULL,
                edited_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
                #patient_status ENUM('Active','Inactive','Deceased') DEFAULT 'Active'
                #access_level = {'admin' : 9, 'consultant' : 8, 'surgeon' : 8, 'doctor' : 7, 'pharmacist' : 6, 'nurse' : 5, 'radiographer' : 5}
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
        passcode_retype = getpass("Retype the password : ")
        if passcode_retype == passcode:
            break
        else:
            print("Passwords do not match.")
    while True:
        try:
            access_level = int(input("Enter access level : "))
            break
        except ValueError:
            print("Enter numbers only.")
    while True:
        try:
            dob_input = input("Enter date of birth (YYYY-MM-DD) : ")
            dob = datetime.strptime(dob_input, "%Y-%m-%d").date()
            break
        except ValueError:
            print("Invalid date format, use YYYY-MM-DD.")
    email = input("Enter email : ")
    phone_no = input("Enter phone number : ")
    query = '''INSERT INTO staff (
    cpr_no, staff_name, designation, department, user_name, passcode, access_level, dob, email, phone_no, edited_by
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                '''
    cur.execute(query, (cpr_no, staff_name, designation, department, user_name, passcode, access_level, dob, email, phone_no, edited_by))
    staff_id = cur.lastrowid
    staff_his_id = staff_id
    cur.execute('''UPDATE staff SET staff_his_id = %s
                where staff_id = %s''',
                (staff_his_id, staff_id))
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
    email = input("Enter patient's email : ")
    phone_no = input("Enter patient's phone number : ")
    address = input("Enter patient's address : ")
    next_of_kin = input("Enter name of patient's 'Next-of'kin' : ")
    relationship = input(f"Enter patient's relationship with {next_of_kin} : ")
    emergency_contact = input("Enter patient's emergency contact : ")

    #--to obtain patient status--

    cur.execute('''SELECT item_id, item_name FROM lookup_code
                WHERE item_category = 'patient_status' and item_if_active = "Yes"''')
    statuses = cur.fetchall()
    print(tabulate(statuses, headers=['ID', 'Status'], tablefmt='pretty'))
    while True:
        try:
            patient_status = int(input("Enter status ID corresponding to the patient : "))
            valid_id = [i[0] for i in statuses]
            if patient_status in valid_id:
                break
        except ValueError:
            print("Enter valid integer.")

    query = '''INSERT INTO patients (
    cpr_no, patient_name, dob, email, phone_no, address, next_of_kin, relationship, emergency_contact, patient_status, edited_by
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    cur.execute(query, (cpr_no, patient_name, dob, email, phone_no, address, next_of_kin, relationship, emergency_contact, patient_status, edited_by))
    patient_id = cur.lastrowid
    patient_his_id = patient_id
    cur.execute('''UPDATE patient SET patient_his_id = %s
                WHERE patient_id = %s)''',
                (patient_his_id, patient_id))
    conn.commit()
    print("Patient record created successfully.")

#--to update staff record--

def update_staff(edited_by):
    while True:
        try:
            staff_id = int(input("Enter the Staff ID you want to update: "))
            break
        except ValueError:
            print("Enter valid integer.")
    cur.execute("SELECT * FROM staff WHERE staff_id = %s AND is_active = 'Yes'", (staff_id,))
    old_data = cur.fetchone()
    if not old_data:
        print("Staff not found.")
        return
    staff_his_id = old_data[1]
    new_version = old_data[13] + 1
    print("Which field do you want to update?")
    print("1) CPR number\n2) Name\n3) Designation\n4) Department\n5) Username\n6) Password\n7) Date-of-birth\n8) Access Level\n9) Email\n10) Phone Number")
    while True:
        try:
            choice = int(input("Enter choice number : "))
            if choice in range(1,11):
                break
            else:
                print("Not valid choice. Try again.")
        except ValueError:
            print("Enter valid integer.")
    new_data = list(old_data[2:13])
    if choice == 1 or choice == 8:
        while True:
            try:
                new_value = int(input("Enter new value : "))
                break
            except ValueError:
                print("Enter valid integer.")
    else:
        new_value = input("Enter new value: ")
    new_data[choice-1] = new_value
    query = '''INSERT INTO staff (staff_his_id, cpr_no, staff_name, designation, department, user_name, passcode, access_level, dob, email, phone_no, version, edited_by)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    cur.execute('''UPDATE staff SET is_active = 'No' WHERE staff_id = %s''', (staff_id,))
    cur.execute(query, (staff_his_id, *new_data, new_version, edited_by))
    conn.commit()
    print("Staff record updated successfully.")

#--to update patient record--

def update_patient(edited_by):
    while True:
        try:
            patient_id = int(input("Enter the patient ID you want to update : "))
            break
        except ValueError:
            print("Enter valid integer.")
    cur.execute('''SELECT * FROM patients WHERE patient_id = %s and is_active = 'Yes' ''', (patient_id,))
    old_data = cur.fetchone()
    if not old_data:
        print("Patient not found.")
        return
    patient_his_id = old_data[1]
    new_version = old_data[14] + 1
    print("Which field do you want to update?")
    print("\n1) CPR number\n2) Name\n3) DOB\n4) Email\n5) Phone number\n 6) Address\n7) Next-of-kin\n8) Relationship with 'Next-of-kin'\n9) Emergency contact")
    while True:
        try:
            choice = int(input("Enter choice number : "))
            if choice in range(1,10):
                break
            else:
                print("Not valid choice. Try again.")
        except ValueError:
            print("Enter a valid integer.")
    new_data = list(old_data[2:12])
    if choice == 1:
        while True:
            try:
                new_value = int(input("Enter new value : "))
                break
            except ValueError:
                print("Enter valid integer.")
    else:
        new_value = input("Enter new value : ")
    new_data[choice-1] = new_value
    query = '''INSERT INTO patients (patient_his_id, cpr_no, patient_name, dob, email, phone_no, address, next_of_kin, relationship, emergency_contact, version, edited_by)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    cur.execute('''UPDATE patients SET is_active = 'No' where patient_id = %s''', (patient_id,))
    cur.execute(query, (patient_his_id, *new_data, new_version, edited_by))
    conn.commit()
    print("Patient record updated successfully.")