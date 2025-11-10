from mysql.connector import connect, Error
from datetime import datetime

try:
    conn = connect(
        host = 'localhost',
        user = 'root',
        password = 'Fawaz@33448113',
        database = 'hospital'
    )
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
                FOREIGN KEY (procedure_id) REFERENCES lookup_table(item_name)
                )''')
except Error as e:
    print(e)

def add_inpatient_procedure(edited_by, patient_id):

    cur.execute('SELECT * from tbl_admission WHERE patient_id = %s', (patient_id,))
    data = cur.fetchall()
    if not data:
        print("No matching patient record found.")

    cur.execute('SELECT * from staff WHERE')
    data = cur.fetchall()
    valid_staff_id = [i[0] for i in data]
    while True:
        try:
            doctor_id = int(input("Enter doctor's ID : "))
            nurse_id = int(input("Enter nurse's ID : "))
            if doctor_id in valid_staff_id and nurse_id in valid_staff_id:
                break
            else:
                print("Could not find either doctor ID or nurse ID. Try again.")
        except ValueError:
            print("Enter only integers.")
    while True:
        try:
            date_input = input("Enter date (YY-MM-DD) and time (HH:MM:SS) : ")
            date_of_procedure = datetime.strptime(date_input, "%Y-%m-%d %H:%M:%S")
            break
        except ValueError:
            print("Invalid date and time format. Try again.")
    while True:
        payment_done = input("Enter yes or no : ").strip().lower()
        consumables_paid = input("Enter yes or no : ").strip().lower()
        if payment_done in ('yes','no') and consumables_paid in ('yes','no'):
            break
        else:
            print("Invalid fields. Try again.")