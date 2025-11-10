from mysql.connector import connect, Error
from tabulate import tabulate
from datetime import datetime
from medication import prescribe_medication

try:
    conn = connect(
        host = 'localhost',
        user = 'root',
        password = 'Fawaz@33448113',
        database = 'hospital'
    )
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS tbl_consultation(
                cons_id INT AUTO_INCREMENT PRIMARY KEY,
                cons_his_id INT,
                appt_id INT,
                doctor_id INT,
                clinic INT,
                cons_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                complaints VARCHAR(500),
                cons_notes VARCHAR(500),
                lab_test ENUM('Yes','No') DEFAULT 'No',
                imaging_test ENUM('Yes','No') DEFAULT 'No',
                discharged ENUM('Yes','No') DEFAULT 'No',
                medication ENUM('Yes','No') DEFAULT 'No',
                version INT DEFAULT 0,
                edited_by INT,
                edited_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (appt_id) REFERENCES appointments(appt_id),
                FOREIGN KEY (doctor_id) REFERENCES staff(staff_id),
                FOREIGN KEY (clinic) REFERENCES lookup_code(item_id)
                )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS tbl_consultationF(
                consF_id INT AUTO_INCREMENT PRIMARY KEY,
                consF_his_id INT,
                cons_id INT,
                consF_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                lab_result VARCHAR(500),
                imaging_result VARCHAR(500),
                diagnosis VARCHAR(500),
                discharged ENUM('Yes','No') DEFAULT 'No',
                medication ENUM('Yes','No') DEFAULT 'No',
                followup ENUM('Yes','No') DEFAULT 'No',
                admission_to_ward ENUM('Yes','No') DEFAULT 'No'),
                version INT DEFAULT 0,
                edited_by INT,
                edited_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cons_id) REFERENCES tbl_consultation(cons_id)
                )''')
except Error as e:
    print(e)

def add_consultation(edited_by, cpr_no):
    cur.execute("""SELECT a.appt_id, p.patient_id, p.cpr_no, p.patient_name, a.doctor_id, a.clinic, a.appt_book_time, s.staff_name
                FROM appointments a
                JOIN patients p ON a.patient_id = p.patient_id
                JOIN staff s ON a.doctor_id = s.staff_id
                WHERE a.appt_is_active = 'Yes' AND p.cpr_no = %s""", (cpr_no,))
    data = cur.fetchall()
    headers = [i[0] for i in cur.description]
    print(tabulate(data, headers=headers, tablefmt='pretty'))

    appt_valid_ids = [i[0] for i in data]
    while True:
        try:
            appt_id = int(input("Enter appointment ID : "))
            if appt_id in appt_valid_ids:
                break
            else:
                print("Enter valid ID.")
        except ValueError:
            print("Enter only integers.")

    selected_appt = [i for i in data if i[0] == appt_id][0]
    doctor_id = selected_appt[4]
    clinic = selected_appt[5]

    complaints = input("Enter patient's complaints : ")
    cons_notes = input("Enter notes from consultation : ")

    while True:
        imaging_test = input("Are you sending for imaging test (Yes/No) : ").lower()
        if imaging_test in ('yes','no'):
            break
        print("Enter only yes or no.")

    while True:
        lab_test = input("Are you sending for lab test? (Yes/No) : ").lower()
        if lab_test in ('yes','no'):
            break
        print("Enter only yes or no.")

    while True:
        discharged = input("Do you want to discharge? (Yes/No) : ").lower()
        if discharged in ('yes','no'):
            break
        print("Enter only yes or no.")

    discharge_flag = False
    if discharged == 'yes' and (imaging_test == 'yes' or lab_test == 'yes'):
        while True:
            confirm = input("You ordered tests. Do you still want to discharge? (Yes/No) : ").lower()
            if confirm in ('yes','no'):
                break
        discharge_flag = confirm == 'yes'
    else:
        discharge_flag = discharged == 'yes'

    while True:
        medication = input("Do you want to prescribe medication (Yes/No) : ").lower()
        if medication in ('yes','no'):
            break
        print("Enter only yes or no.")

    cur.execute('''INSERT INTO tbl_consultation 
                   (appt_id, doctor_id, clinic, complaints, cons_notes, lab_test, imaging_test, discharged, medication, edited_by)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                (appt_id, doctor_id, clinic, complaints, cons_notes, lab_test.capitalize(), imaging_test.capitalize(),
                 'Yes' if discharge_flag else 'No', medication.capitalize(), edited_by))

    cons_id = cur.lastrowid
    cons_his_id = cons_id
    cur.execute('''UPDATE tbl_consultation SET cons_his_id = %s WHERE cons_id = %s''', (cons_his_id, cons_his_id))

    if discharge_flag:
        cur.execute('''UPDATE appointments 
                       SET appt_if_active = 'No', edited_by = %s 
                       WHERE appt_id = %s''', (edited_by, appt_id))
        if medication == 'yes':
            prescribe_medication(edited_by)
    else:
        cur.execute('''INSERT INTO tbl_consultationF 
                       (cons_id, discharged, medication, edited_by)
                       VALUES (%s, 'No', %s, %s)''',
                    (cons_id, medication.capitalize(), edited_by))
        print("Follow-up record created in tbl_consultationF.")

def manage_followup(edited_by, cpr_no):
    cur.execute('''
        SELECT c.cons_id, a.appt_id, p.patient_name, s.staff_name, c.discharged, c.medication
        FROM tbl_consultation c
        JOIN appointments a ON c.appt_id = a.appt_id
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN staff s ON a.doctor_id = s.staff_id
        WHERE p.cpr_no = %s
    ''', (cpr_no,))
    
    data = cur.fetchall()
    if not data:
        print("No consultations found for this patient.")
        return
    
    headers = [i[0] for i in cur.description]
    print(tabulate(data, headers=headers, tablefmt='pretty'))

    cons_ids = [i[0] for i in data]
    while True:
        try:
            cons_id = int(input("Enter consultation ID to manage follow-up: "))
            if cons_id in cons_ids:
                break
            else:
                print("Enter a valid consultation ID.")
        except ValueError:
            print("Enter only integers.")

    selected_cons = [i for i in data if i[0] == cons_id][0]
    cons_id = selected_cons[0]
    appt_id = selected_cons[1]
    discharged = selected_cons[4]

    lab_result = input("Enter lab results (leave blank if none) : ")
    imaging_result = input("Enter imaging results (leave blank if none) : ")
    diagnosis = input("Enter diagnosis notes : ")

    while True:
        admission_to_ward = input("Admit patient to ward? (Yes/No) : ").lower()
        if admission_to_ward in ('yes', 'no'):
            break
        print("Enter only Yes or No.")
    if admission_to_ward == 'no':
        discharged = 'yes'
        cur.execute('''UPDATE tbl_consultation SET discharged = 'Yes' where cons_id = %s''', (cons_id,))
        cur.execute('''UPDATE appointments set appt_is_active = 'No' where appt_id = %s''', (appt_id,))
    while True:
        medication = input("Prescribe medication? (Yes/No): ").lower()
        if medication in ('yes', 'no'):
            break
        print("Enter only 'Yes' or 'No'.")
    if medication == 'yes':
        prescribe_medication(edited_by)

    cur.execute('''INSERT INTO tbl_consultationF (
                cons_id, lab_result, imaging_result, diagnosis, discharged, medication, admission_to_ward, edited_by) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', 
                (cons_id, lab_result, imaging_result, diagnosis, 'Yes' if discharged.lower() == 'yes' else 'No', 
                 medication.capitalize(), admission_to_ward.capitalize(), edited_by))
    consF_id = cur.lastrowid
    consF_his_id = consF_id
    cur.execute('''UPDATE tbl_consultationsF set consF_his_id = %s where consF_id = %s''', (consF_his_id, consF_id))

    print("Follow-up consultation record added successfully.")
    if admission_to_ward == 'yes':
        print("Triggering admission process...")