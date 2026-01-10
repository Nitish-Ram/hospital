from mysql.connector import connect, Error
from tabulate import tabulate
from datetime import datetime

try:
    conn= connect(host="localhost", user="root", password="Fawaz@33448113",database="hospital")

    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS medication (
                med_id INT AUTO_INCREMENT PRIMARY KEY,
                med_his_id INT,
                cons_id INT NULL,
                adm_id INT NULL,
                medicine INT,
                quantity INT,
                dose VARCHAR(100),
                instruction VARCHAR(200),
                valid_until DATE,
                medication_is_active ENUM('Yes','No') DEFAULT 'Yes',
                version INT DEFAULT 0,
                edited_by INT NULL,
                edited_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (medicine) REFERENCES inventories(inv_id),
                FOREIGN KEY (cons_id) REFERENCES tbl_consultation(cons_id),
                FOREIGN KEY (adm_id) REFERENCES tbl_admission(adm_id)
                )''')
except Error as e:
    print(e)

def prescribe_medication_cons(cons_id, edited_by):
    try:
        cur.execute("SELECT inv_id, inv_name, inv_category FROM inventories WHERE inv_if_active='Yes'")
        medicines = cur.fetchall()
        if not medicines:
            print("No medicines available in inventory.")
            return
        headers = [i[0] for i in cur.description]
        print(tabulate(medicines, headers=headers, tablefmt='pretty'))
        valid_ids = [i[0] for i in medicines]
        while True:
            try:
                medicine = int(input("Enter Medicine ID: "))
                if medicine in valid_ids:
                    break
                else:
                    print("Enter a valid Medicine ID from the list above.")
            except ValueError:
                print("Enter only integers.")
        while True:
            try:
                quantity = int(input("Enter Quantity: "))
                break
            except ValueError:
                print("Enter only integers for quantity.")
        dose = input("Enter Dose : ")
        instruction = input("Enter Instruction : ")
        while True:
            valid_until = input("Enter Valid Until (YYYY-MM-DD): ")
            try:
                datetime.strptime(valid_until, "%Y-%m-%d")
                break
            except ValueError:
                print("Invalid date format. Enter in YYYY-MM-DD format.")
        query = """INSERT INTO medication (cons_id, medicine, quantity, dose, instruction, valid_until, edited_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        conn.commit()
        cur.execute(query, ( cons_id, medicine, quantity,
            dose, instruction, valid_until,
            edited_by))
        med_id = cur.lastrowid
        med_his_id = med_id
        cur.execute("UPDATE medication SET med_his_id=%s WHERE med_id=%s", (med_his_id ,med_id))
        conn.commit()
    except Exception as e:
        print(" Error adding medication:", e)

def prescribe_medication_adm(adm_id, edited_by):
    try:
        cur.execute("SELECT inv_id, inv_name, inv_category FROM inventories WHERE inv_if_active='Yes'")
        medicines = cur.fetchall()
        if not medicines:
            print("No medicines available in inventory.")
            return
        headers = [i[0] for i in cur.description]
        print(tabulate(medicines, headers=headers, tablefmt='pretty'))
        valid_ids = [i[0] for i in medicines]
        while True:
            try:
                medicine = int(input("Enter Medicine ID: "))
                if medicine in valid_ids:
                    break
                else:
                    print("Enter a valid Medicine ID from the list above.")
            except ValueError:
                print("Enter only integers.")
        while True:
            try:
                quantity = int(input("Enter Quantity: "))
                break
            except ValueError:
                print("Enter only integers for quantity.")
        dose = input("Enter Dose : ")
        instruction = input("Enter Instruction : ")
        while True:
            valid_until = input("Enter Valid Until (YYYY-MM-DD): ")
            try:
                datetime.strptime(valid_until, "%Y-%m-%d")
                break
            except ValueError:
                print("Invalid date format. Enter in YYYY-MM-DD format.")
        query = """INSERT INTO medication (adm_id, medicine, quantity, dose, instruction, valid_until, edited_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        cur.execute(query, ( adm_id, medicine, quantity,
            dose, instruction, valid_until,
            edited_by))
        med_id = cur.lastrowid
        med_his_id = med_id
        cur.execute("UPDATE medication SET med_his_id=%s WHERE med_id=%s", (med_his_id ,med_id))
        conn.commit()
    except Exception as e:
        print(" Error adding medication:", e)

def view_medications(cpr_no):
    type = input("View medications for 1.Consultation 2.Admission\n>").strip()
    if type == '1':
        cur.execute('''SELECT p.patient_name,m.cons_id,m.medicine, m.quantity, m.dose, m.instruction
                        FROM medication m
                        JOIN tbl_consultation c ON m.cons_id = c.cons_id
                        JOIN appointments a ON c.appt_id = a.appt_id
                        JOIN patients p ON a.patient_id = p.patient_id
                        WHERE p.cpr_no = %s AND m.medication_is_active = 'Yes'
                        AND adm_id is NULL ''', (cpr_no,))
        data=cur.fetchall()
        headers = [i[0] for i in cur.description]
        print(tabulate(data, headers = headers, tablefmt = 'pretty'))
        
    elif type == '2':
        cur.execute('''SELECT p.patient_name, m.adm_id, m.medicine, m.quantity, m.dose, m.instruction
                        FROM medication m
                        JOIN tbl_admission ad ON m.adm_id = ad.adm_id
                        JOIN patients p ON ad.patient_id = p.patient_id
                        WHERE p.cpr_no = %s AND m.medication_is_active = 'Yes' ''', (cpr_no,))
        data=cur.fetchall()
        headers = [i[0] for i in cur.description]
        print(tabulate(data, headers = headers, tablefmt = 'pretty'))
    else:
        print("Invalid choice")