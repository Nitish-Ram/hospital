from mysql.connector import connect, Error
from tabulate import tabulate
from datetime import time

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
                cons_date DATE,
                complaints VARCHAR(500),
                diagnosis VARCHAR(500),
                cons_notes VARCHAR(500),
                lab_test ENUM('Yes','No') DEFAULT 'No',
                imaging_test ENUM('Yes','No') DEFAULT 'No',
                medication ENUM('Yes','No') DEFAULT 'No',
                discharged ENUM('Yes','No') DEFAULT 'No',
                admission_to_ward ENUM('Yes','No') DEFAULT 'No',
                followup_date DATE,
                version INT DEFAULT 0,
                edited_by INT,
                edited_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (appt_id) REFERENCES appointments(appt_id),
                FOREIGN KEY (doctor_id) REFERENCES staff(staff_id),
                FOREIGN KEY (clinic) REFERENCES lookup_code(item_id)
                )''')
except Error as e:
    print(e)

def add_consultation(edited_by):
    try:
        appt_id = int(input("Enter Appointment ID: "))
        doctor_id = int(input("Enter Doctor ID: "))
        clinic = int(input("Enter Clinic Code: "))
        cons_date = input("Enter Consultation Date (YYYY-MM-DD): ")
        complaints = input("Enter Patient Complaints: ")
        diagnosis = input("Enter Diagnosis: ")
        cons_notes = input("Enter Consultation Notes: ")
        #yes or no qs
        lab_test = input("Lab Test Required? (Yes/No): ")
        imaging_test = input("Imaging Test Required? (Yes/No): ")
        medication = input("Medication Prescribed? (Yes/No): ")
        discharged = input("Discharged? (Yes/No): ")
        admission_to_ward = input("Admit to Ward? (Yes/No): ")
        followup_date = input("Enter Follow-up Date (YYYY-MM-DD or leave blank): ")
        if followup_date.isspace():followup_date=None

        query = """
        INSERT INTO tbl_consultation ( appt_id, doctor_id, clinic, cons_date,
            complaints, diagnosis, cons_notes, lab_test, imaging_test,
            medication, discharged, admission_to_ward, followup_date,
            edited_by
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cur.execute(query, (
            appt_id, doctor_id, clinic, cons_date,
            complaints, diagnosis, cons_notes, lab_test, imaging_test,
            medication, discharged, admission_to_ward, followup_date,
            edited_by
        ))

        cons_id=cur.lastrowid

        cur.execute("UPDATE tbl_consultation SET cons_his_id=%s where cons_id=%s",(cons_id,cons_id))

        conn.commit()

    except Exception as e:
        print(" Error adding consultation:", e)

def view_all_consultations():
    try:
        cur.execute("SELECT * FROM tbl_consultation")
        rows = cur.fetchall()

        if rows:
            headers = [i[0] for i in cur.description]
            print(tabulate(rows, headers=headers, tablefmt="pretty"))
        else:
            print(" No consultations found.")
    except Exception as e:
        print(" Error viewing consultations:", e)

def search_consultation():
    try:

        cons_id = int(input("Enter Consultation ID to search: "))

        cur.execute("SELECT * FROM tbl_consultation WHERE cons_id = %s", (cons_id,))
        row = cur.fetchone()

        if row:
            headers = [i[0] for i in cur.description]
            print(tabulate([row], headers=headers, tablefmt="pretty"))
        else:
            print(" Consultation not found.")

    except Exception as e:
        print(" Error searching consultation:", e)

def update_consultation():
    try:
        cons_id = int(input("Enter Consultation ID to update: "))
        cur.execute("SELECT * from tbl_consultation where cons_id=%s",(cons_id,))
        old_data=cur.fetchone()
        if not old_data:
            print("consultaion not found")
            return
        print("press enter if you do not want to update")
        diagnosis = input("Enter new Diagnosis: ")
        notes = input("Enter new Notes: ")
        if diagnosis.isspace(): diagnosis=old_data[7]
        if notes.isspace():notes=old_data[8]
        edited_by=old_data[-2]
        new_data=list(old_data[1:-3])
        new_data[6],new_data[7]=diagnosis,notes
        
        query='''INSERT INTO tbl_consultaions(cons_his_id,appt_id, doctor_id, clinic, cons_date,
            complaints, diagnosis, cons_notes, lab_test, imaging_test,
            medication, discharged, admission_to_ward, followup_date,
            edited_by) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        cur.execute(query,*new_data,edited_by)
        conn.commit()
        
    except Exception as e:
        print(" Error updating consultation:", e)
def delete_consultation():
    try:
        cons_id = int(input("Enter Consultation ID to delete: "))
        cur.execute("DELETE FROM tbl_consultation WHERE cons_id = %s", (cons_id,))
        conn.commit()

    except Exception as e:
        print(" Error deleting consultation:", e)