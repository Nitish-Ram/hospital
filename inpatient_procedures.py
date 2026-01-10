from mysql.connector import connect, Error
from datetime import datetime
from tabulate import tabulate
from db_config import config

try:
    conn = config()
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS inpatient_procedures (
                ipp_id INT AUTO_INCREMENT PRIMARY KEY,
                ipp_his_id INT,
                adm_id INT,
                procedure_id INT,
                date_of_procedure DATETIME,
                doctor_id INT,
                nurse_id INT,
                payment_done ENUM('Yes','No') DEFAULT 'No',
                consumables_paid ENUM('Yes','No') DEFAULT 'No',
                version INT DEFAULT 0,
                edited_by INT NULL,
                edited_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (adm_id) REFERENCES tbl_admission(adm_id),
                FOREIGN KEY (doctor_id) REFERENCES staff(staff_id),
                FOREIGN KEY (nurse_id) REFERENCES staff(staff_id),
                FOREIGN KEY (procedure_id) REFERENCES lookup_code(item_id)
                )''')
    
    conn.commit()

except Error as e:
    print(e)

def add_inpatient_procedure(edited_by, cpr_no):
    cur.execute("""SELECT a.adm_id, p.patient_name, p.cpr_no, a.adm_date, s.staff_name
                FROM tbl_admission a JOIN patients p ON a.patient_id = p.patient_id
                JOIN staff s ON a.adm_doctor = s.staff_id WHERE p.cpr_no = %s 
                AND a.adm_id NOT IN (SELECT adm_id FROM tbl_discharge)""", (cpr_no,))
    admission = cur.fetchone()
    if not admission:
        print("No active admission found for this patient.")
        return

    adm_id = admission[0]
    patient_name = admission[1]
    adm_date = admission[3]
    doctor_name = admission[4]

    print(f"Patient: {patient_name}, Admission Date: {adm_date}, Doctor: {doctor_name}")
        
    cur.execute("""SELECT item_id, item_name FROM lookup_code WHERE item_category='SurgicalProcedure' AND item_if_active='Yes'""")
    
    procedures = cur.fetchall()
    print("\nAvailable Procedures : ")
    for i in procedures:
        print(f"{i[0]}. {i[1]}")
    
    while True:
        try:
            procedure_id = int(input("Enter procedure ID: "))
            if procedure_id in [i[0] for i in procedures]:
                break
            else:
                print("Invalid procedure ID.")
        except ValueError:
            print("Enter only integers.")

    cur.execute("SELECT staff_id, staff_name, designation FROM staff WHERE is_active='Yes'")
    staff_list = cur.fetchall()

    print("\nAvailable Staff:")
    headers = ['ID', 'Name', 'Designation']
    print(tabulate(staff_list, headers=headers, tablefmt='pretty'))

    while True:
        try:
            doctor_id = int(input("Enter doctor's staff ID: "))
            nurse_id = int(input("Enter nurse's staff ID: "))
            if doctor_id in [i[0] for i in staff_list] and nurse_id in [i[0] for i in staff_list]:
                break
            else:
                print("Could not find staff IDs. Try again.")
        except ValueError:
            print("Enter only integers.")
    
    while True:
        try:
            date_input = input("Enter date and time (YYYY-MM-DD HH:MM:SS): ")
            date_of_procedure = datetime.strptime(date_input, "%Y-%m-%d %H:%M:%S")
            break
        except ValueError:
            print("Invalid date and time format. Try YYYY-MM-DD HH:MM:SS.")
    
    while True:
        payment_done = input("Payment done (Yes/No): ").lower()
        if payment_done in ('yes', 'no'):
            payment_done = payment_done.capitalize()
            break
        print("Enter only Yes or No.")
    
    while True:
        consumables_paid = input("Consumables paid (Yes/No): ").lower()
        if consumables_paid in ('yes', 'no'):
            consumables_paid = consumables_paid.capitalize()
            break
        print("Enter only Yes or No.")
    
    cur.execute("""
                INSERT INTO inpatient_procedures (adm_id, procedure_id, date_of_procedure, doctor_id, nurse_id, payment_done, consumables_paid, edited_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (adm_id, procedure_id, date_of_procedure, doctor_id, nurse_id, payment_done, consumables_paid, edited_by))
    ipp_id = cur.lastrowid
    cur.execute("UPDATE inpatient_procedures SET ipp_his_id=%s WHERE ipp_id=%s", (ipp_id, ipp_id))
    conn.commit()
    print("Inpatient procedure recorded successfully.")

def view_procedures(cpr_no):
    cur.execute('''SELECT ip.ipp_id, ip.adm_id, l.item_name AS procedure_name, ip.date_of_procedure,
                d.staff_name AS doctor_name, n.staff_name AS nurse_name, ip.payment_done, ip.consumables_paid
                FROM inpatient_procedures ip
                INNER JOIN tbl_admission a ON ip.adm_id = a.adm_id
                INNER JOIN patients p ON a.patient_id = p.patient_id
                LEFT JOIN staff d ON ip.doctor_id = d.staff_id
                LEFT JOIN staff n ON ip.nurse_id = n.staff_id
                INNER JOIN lookup_code l ON ip.procedure_id = l.item_id
                WHERE p.cpr_no = %s''', (cpr_no,))
    data = cur.fetchall()
    if not data:
        print("Could not find any procedures done.")
    headers = [i[0] for i in cur.description]
    print(tabulate(data, headers=headers, tablefmt='pretty'))