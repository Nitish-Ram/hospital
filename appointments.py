from mysql.connector import connect, Error
from tabulate import tabulate
from datetime import datetime
from db_config import config

try:
    conn = config()
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS appointments (
                appt_id INT AUTO_INCREMENT PRIMARY KEY,
                appt_his_id INT,
                patient_id INT,
                doctor_id INT,
                clinic INT,
                appt_book_time DATETIME,
                cons_fee_paid ENUM('Yes','No') DEFAULT 'No',
                cons_payment_receiptno INT,
                cons_paid_amount VARCHAR(100),
                appt_is_active ENUM('Yes','No') DEFAULT 'Yes',
                if_followup ENUM('Yes','No') DEFAULT 'No',
                version INT DEFAULT 0,
                edited_by INT NULL,
                edited_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
                FOREIGN KEY (doctor_id) REFERENCES staff(staff_id),
                FOREIGN KEY (clinic) REFERENCES lookup_code(item_id)
                )''')
    
    conn.commit()

except Error as e:
    print(e)

def view_all_appointment():
    cur.execute("""SELECT a.appt_id, p.patient_id, p.cpr_no, p.patient_name, a.doctor_id, a.clinic, a.appt_book_time, s.staff_name
                FROM appointments a
                JOIN patients p ON a.patient_id = p.patient_id
                JOIN staff s ON a.doctor_id = s.staff_id
                WHERE a.appt_is_active = 'Yes'""")
    data = cur.fetchall()
    headers = [i[0] for i in cur.description]
    print(tabulate(data, headers = headers, tablefmt= 'pretty'))

def view_appointment(cpr_no):
    cur.execute("""SELECT a.appt_id, p.patient_id, p.cpr_no, p.patient_name, a.doctor_id, a.clinic, a.appt_book_time, s.staff_name
                FROM appointments a
                JOIN patients p ON a.patient_id = p.patient_id
                JOIN staff s ON a.doctor_id = s.staff_id
                WHERE a.appt_is_active = 'Yes' and p.cpr_no = %s""", (cpr_no,))
    data = cur.fetchall()
    headers = [i[0] for i in cur.description]
    print(tabulate(data, headers = headers, tablefmt = 'pretty'))

def book_appointment(edited_by, cpr_no):
    cur.execute("""SELECT patient_id, patient_name FROM patients WHERE cpr_no = %s""", (cpr_no,))
    patient = cur.fetchone()
    if not patient:
        print("No patient found with this CPR number.")
        return
    patient_id = patient[0]

    cur.execute("""SELECT item_id, item_name from lookup_code
                WHERE item_category = 'Location' and item_if_active = 'Yes'""")
    clinics = cur.fetchall()
    print("Available clinics")
    for i in clinics:
        print(f"{i[0]} . {i[1]}")

    while True:
        try:
            clinic_id = int(input("Enter clinic ID : "))
            if clinic_id in [i[0] for i in clinics]:
                break
            else:
                print("Couldn't find clinic. Try again.")
        except ValueError:
            print("Enter only integers.")

    cur.execute('''SELECT staff_id, staff_name ,department FROM staff
                WHERE designation = 'Doctor' ''')
    doctors = cur.fetchall()
    print("\nAvailable doctors")
    print('''606	Neurology
607	ENT
608	Cardiology
609	Cardio Thoracic surgery
610	General Medicine
611	General Surgery
612	Orthopedics
613	Nephrology
614	Urology
615	Gynecology''')
    for i in doctors:
        
        print(f"{i[0]} . {i[1]} . {i[2]}")

    while True:
        try:
            doctor_id = int(input("Enter doctor ID : "))
            if doctor_id in [i[0] for i in doctors]:
                break
            else:
                print("Couldn't find doctors. Try again.")
        except ValueError:
            print("Enter only integers.")
            
    while True:
        try:
            date_input = input("Enter date (YYYY-MM-DD) and time (HH:MM:SS) : ")
            appt_book_time = datetime.strptime(date_input, "%Y-%m-%d %H:%M:%S")
            break
        except ValueError:
            print("Invalid date and time format. Try again.")

    while True:
        cons_fee_paid = input("Enter if fees were paid (Yes/No) : ").lower()
        if cons_fee_paid in ('yes', 'no'):
            break
        else:
            print("Enter valid option.")

    while True:
        try:
            cons_fee_amount = float(input("Enter paid amount : "))
            break
        except ValueError:
            print("Enter only numbers.")

    cur.execute('''INSERT INTO appointments (
                patient_id, doctor_id, clinic, appt_book_time, cons_fee_paid, cons_paid_amount, edited_by) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                (patient_id, doctor_id, clinic_id, appt_book_time, cons_fee_paid.capitalize(), cons_fee_amount, edited_by))
    appt_his_id = cur.lastrowid
    cur.execute('''UPDATE appointments SET appt_his_id = %s WHERE appt_id = %s''', (appt_his_id, appt_his_id))
    conn.commit()

def update_appointment(edited_by, cpr_no):
    cur.execute("SELECT patient_id, patient_name FROM patients WHERE cpr_no = %s", (cpr_no,))
    patient = cur.fetchone()
    if not patient:
        print("No patient found with this CPR number.")
        return
    patient_id = patient[0]

    cur.execute("""SELECT appt_id, appt_book_time, clinic FROM appointments
                WHERE patient_id = %s and appt_is_active = 'Yes'""", (patient_id,))
    data = cur.fetchall()
    header = [i[0] for i in cur.description]
    if not data:
        print("Couldn't find any active appointments.")
    else:
        print(tabulate(data, headers = header, tablefmt = 'pretty'))

    while True:
        try:
            appt_id = int(input("Enter appointment ID to update : "))
            if appt_id in [i[0] for i in data]:
                break
            else:
                print("Enter a valid appointment ID.")
        except ValueError:
            print("Enter only integers.")
    cur.execute('''SELECT appt_his_id, patient_id, doctor_id, clinic, appt_book_time, cons_fee_paid, cons_paid_amount, version
                FROM appointments where appt_id = %s''', (appt_id,))
    old_data = list(cur.fetchone())

    while True:
        ch = input("1) Change doctor \n2) Change booked time\n3) Change paid amount\nEnter choice : ")
        if ch not in '123':
            print("Enter only 1,2 or 3")
        else:
            break

    if ch == '1':
        clinic_id = [i[2] for i in data if i[0] == appt_id][0]
        cur.execute("SELECT item_name FROM lookup_code WHERE item_id = %s", (clinic_id,))
        clinic_name = cur.fetchone()[0]

        cur.execute('''SELECT staff_id, staff_name from staff
                    WHERE designation = 'Doctor' and department = %s''', (clinic_name,))
        doctors = cur.fetchall()
        print("Available doctors.")
        for i in doctors:
            print(f"{i[0]} . {i[1]}")

        while True:
            try:
                new_doctor = int(input("Enter new doctor ID : "))
                if new_doctor in [i[0] for i in doctors]:
                    break
                else:
                    print("Enter valid doctor ID.")
            except ValueError:
                print("Enter only integers.")
        old_data[2] = new_doctor
        old_data[-1] += 1

    elif ch == '2':
        while True:
            try:
                date_input = input("Enter new date (YY-MM-DD) and time (HH:MM:SS) : ")
                new_cons_date = datetime.strptime(date_input, "%Y-%m-%d %H:%M:%S")
                break
            except ValueError:
                print("Invalid date and time format. Try again.")
        old_data[4] = new_cons_date
        old_data[-1] += 1
    
    elif ch == '3':
        new_paid_amount = input("Enter new amount : ")
        old_data[-2] = new_paid_amount
        old_data[-1] += 1

    cur.execute('''INSERT into appointments (
                appt_his_id, patient_id, doctor_id, clinic, appt_book_time, cons_fee_paid, cons_paid_amount, version, edited_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''',(*old_data, edited_by))
    cur.execute('''UPDATE appointments SET appt_is_active = 'No'
                WHERE appt_id = %s''', (appt_id,))
    conn.commit()
    
def delete_appointment(edited_by, cpr_no):
    cur.execute("SELECT patient_id, patient_name FROM patients WHERE cpr_no = %s", (cpr_no,))
    patient = cur.fetchone()
    if not patient:
        print("No patient found with this CPR number.")
        return
    patient_id = patient[0]

    cur.execute("""SELECT appt_id, appt_book_time, clinic FROM appointments
                WHERE patient_id = %s and appt_is_active = 'Yes'""", (patient_id,))
    data = cur.fetchall()
    header = [i[0] for i in cur.description]
    if not data:
        print("Couldn't find any active appointments.")
    else:
        print(tabulate(data, headers = header, tablefmt = 'pretty'))
        for i in data:
            print(f"{i[0]} . {i[1]}")

    while True:
        try:
            appt_id = int(input("Enter appointment ID to update : "))
            if appt_id in [i[0] for i in data]:
                break
            else:
                print("Enter a valid appointment ID.")
        except ValueError:
            print("Enter only integers.")
    cur.execute('''UPDATE appointments SET appt_is_active = 'No', edited_by = %s
                WHERE appt_id = %s''', (edited_by, appt_id))
    conn.commit()