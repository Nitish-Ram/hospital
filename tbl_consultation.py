from mysql.connector import connect, Error
from tabulate import tabulate
from datetime import datetime

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
                followup ENUM('Yes','No') DEFAULT 'No'
                admission_to_ward ENUM('Yes','No') DEFAULT 'No'),
                version INT DEFAULT 0,
                edited_by INT,
                edited_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cons_id) REFERENCES tbl_consultation(cons_id)
                )''')
except Error as e:
    print(e)

def add_consultation(edited_by):
    try:
        appt_id = int(input("Enter Appointment ID: "))

        while True:
            try:
                date_input = input("Enter date (YY-MM-DD) and time (HH:MM:SS) : ")
                cons_date = datetime.strptime(date_input, "%Y-%m-%d %H:%M:%S")
                break
            except ValueError:
                print("Invalid date and time format. Try again.")
        complaints = input("Enter Patient Complaints: ")
        diagnosis = input("Enter Diagnosis: ")
        cons_notes = input("Enter Consultation Notes: ")

        #yes/no questions

        diagnostic_q = ["Lab test required?", 
                        "Imaging test required?",
                        "Medication prescribed?"]
        diagnostic_a = []
        for i in diagnostic_q:
            while True:
                answer = input(f"{i} (Yes/No) : ").lower().strip()
                if answer in ('yes','no'):
                    diagnostic_a.append(answer)
                    break
                else:
                    print("Enter only yes or no.")
        lab_test = diagnostic_a[0]
        imaging_test = diagnostic_a[1]
        #needs to come back for the second time (second table to be activated)
        medication = diagnostic_a[2]
        
        while True:
            discharged = input("Patient discharged? (Yes/No)").strip().lower()
            if discharged in ('yes','no'):
                break
            else:
                print("Enter only yes or no.")
        
        admission_to_ward = input("Admit to Ward? (Yes/No): ")
        #tbl_admission

    except Exception as e:
        print(" Error adding consultation:", e)

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