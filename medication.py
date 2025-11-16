from mysql.connector import connect, Error
from tabulate import tabulate
from datetime import datetime

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

    cur.execute('''CREATE TABLE IF NOT EXISTS medication (
                med_id INT AUTO_INCREMENT PRIMARY KEY,
                med_his_id INT,
                cons_id INT,
                adm_id INT,
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

def prescribe_medication(cons_id, edited_by, adm_id = None):
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
        cur.execute(query, ( cons_id, medicine, quantity,
            dose, instruction, valid_until,
            edited_by))
        med_id = cur.lastrowid
        med_his_id = med_id
        cur.execute("UPDATE medication SET med_his_id=%s WHERE med_id=%s", (med_his_id ,med_id))
        conn.commit()
    except Exception as e:
        print(" Error adding medication:", e)

def update_medication(edited_by, cpr_no):
    cur.execute('''SELECT m.med_id, m.cons_id, m.medicine, m.quantity, m.dose, m.instruction, m.valid_until, m.edited_by, m.edited_on, m.version
                   FROM medication m
                   JOIN tbl_consultation c ON m.cons_id = c.cons_id
                   JOIN appointments a ON c.appt_id = a.appt_id
                   JOIN patients p ON a.patient_id = p.patient_id
                   WHERE p.cpr_no = %s''', (cpr_no,))
    
    data = cur.fetchall()
    if not data:
        print("No medications found for this patient.")
        return

    valid_ids = [i[0] for i in data]
    headers = [i[0] for i in cur.description]
    print(tabulate(data, headers=headers, tablefmt='pretty'))

    while True:
        try:
            med_id = int(input("Enter Medication ID to update : "))
            if med_id in valid_ids:
                break
            else:
                print("Medication not found. Try again.")
        except ValueError:
            print("Enter only integers.")

    cur.execute('''SELECT * FROM medication WHERE med_id = %s''', (med_id,))
    old_data = cur.fetchone()
    med_his_id = old_data[1]
    new_version = old_data[9] + 1
    new_data = list(old_data[3:7])

    print("Enter value to update.")
    print("1) Quantity\n2) Dose\n3) Instruction\n4) Valid Until")
    while True:
        try:
            choice = int(input("Enter required value : "))
            if choice in range(1,5):
                break
            else:
                print("Enter correct value. Try again.")
        except ValueError:
            print("Enter only integers.")

    if choice == 1:
        while True:
            try:
                new_value = int(input("Enter updated quantity : "))
                break
            except ValueError:
                print("Enter only integers.")
    elif choice == 4:
        while True:
            try:
                new_value_input = input("Enter Valid Until date (YYYY-MM-DD) : ")
                new_value = datetime.strptime(new_value_input, "%Y-%m-%d").date()
                break
            except ValueError:
                print("Invalid date format, use YYYY-MM-DD.")
    else:
        new_value = input("Enter updated value : ")

    new_data[choice-1] = new_value
    cur.execute('''UPDATE medication SET medication_is_active = 'No' WHERE med_id = %s''', (med_id,))

    cur.execute('''INSERT INTO medication (med_his_id, quantity, dose, instruction, valid_until, version, edited_by)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                (med_his_id, *new_data, new_version, edited_by))
    conn.commit()
    print("Medication updated successfully.")