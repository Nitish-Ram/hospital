from mysql.connector import connect, Error
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


    cur.execute('''CREATE TABLE IF NOT EXISTS tbl_admission(
                adm_id INT AUTO_INCREMENT PRIMARY KEY,
                adm_his_id INT,
                patient_id INT,
                adm_date DATETIME,
                adm_doctor INT,
                ward INT,
                payment ENUM('Yes','No') DEFAULT 'No',
                version INT DEFAULT 0,
                edited_by INT NULL,
                edited_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
                FOREIGN KEY (adm_doctor) REFERENCES staff(staff_id),
                FOREIGN KEY (ward) REFERENCES lookup_code(item_id)
                )''')
except Error as e:
    print(e)

def add_admission(edited_by, cpr_no):
    cur.execute('''SELECT patient_id, patient_name from patients
                WHERE cpr_no = %s''', (cpr_no,))
    patients = cur.fetchone()
    if not patients:
        print("Could not find a patient with the following CPR number.")
        return
    patient_id = patients[0]
    patient_name = patients[1]

    cur.execute("SELECT staff_id, staff_name from staff WHERE designation ='physician' OR designation = 'surgeon'")
    staff = cur.fetchall()
    print(tabulate(staff, headers=["Staff ID", "Staff Name"], tablefmt="pretty"))
    valid_ids = [i[0] for i in staff]
    while True:
        try:
            staff_id = int(input("Enter staff ID : "))
            if staff_id in valid_ids:
                break
            else:
                print("Could not find staff. Try again.")
        except ValueError:
            print("Enter only integers.")

    while True:
        try:
            date_input = input("Enter date (YYYY-MM-DD) and time (HH:MM:SS) : ")
            adm_book_time = datetime.strptime(date_input, "%Y-%m-%d %H:%M:%S")
            break
        except ValueError:
            print("Invalid date and time format. Try again.")

    cur.execute('''SELECT item_id, item_name
                FROM lookup_code
                WHERE item_category = 'Bed'
                AND item_id NOT IN
                (SELECT t.ward FROM tbl_admission t LEFT JOIN tbl_discharge d ON t.adm_id = d.adm_id WHERE d.discharge_date IS NULL)''')
    beds = cur.fetchall()
    if not beds:
        print("No beds available for admission at the moment.")
        return
    valid_bed_ids = [i[0] for i in beds]
    while True:
        try:
            bed_id = int(input("Enter bed to admit : "))
            if bed_id in valid_bed_ids:
                break
            else:
                print("Enter valid bed ID.")
        except ValueError:
            print("Enter integers only.")
    
    while True:
        payment = input("Enter if payment is done (Yes/No) : ").lower()
        if payment in ('yes', 'no'):
            break
        else:
            print("Enter only Yes or No.")
    
    cur.execute("""INSERT INTO tbl_admission (patient_id, adm_date, adm_doctor, ward, payment, edited_by)
                VALUES (%s, %s, %s, %s, %s, %s)""",
                (patient_id, adm_book_time, staff_id, bed_id, payment.capitalize(), edited_by))
    adm_his_id = cur.lastrowid
    cur.execute("""UPDATE tbl_admission SET adm_his_id = %s WHERE adm_id = %s""", (adm_his_id, adm_his_id))
    print(f"Patient {patient_name} admitted successfully to bed {bed_id}.")

def view_all_admissions():
    cur.execute('''SELECT p.cpr_no, p.patient_name, l.item_name AS bed FROM tbl_admission a
                INNER JOIN patients p ON a.patient_id = p.patient_id 
                LEFT JOIN tbl_discharge d ON a.adm_id = d.adm_id
                INNER JOIN lookup_code l ON a.ward = l.item_id 
                WHERE d.discharge_date IS NULL''')
    data = cur.fetchall()
    headers = [i[0] for i in cur.description]
    print(tabulate(data,headers = headers, tablefmt = 'pretty'))

def view_admission(cpr_no):
    cur.execute('''SELECT p.cpr_no, p.patient_name, l.item_name AS bed FROM tbl_admission a
                INNER JOIN patients p ON a.patient_id = p.patient_id 
                LEFT JOIN tbl_discharge d ON a.adm_id = d.adm_id
                INNER JOIN lookup_code l ON a.ward = l.item_id 
                WHERE d.discharge_date IS NULL
                AND p.cpr_no = %s''', (cpr_no,))
    data = cur.fetchall()
    if not data:
        print("Could not find any admissions.")
        return
    headers = [i[0] for i in cur.description]
    print(tabulate(data, headers=headers, tablefmt='pretty'))