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

def prescribe_medication(edited_by):
    try:
        #for now
        cons_id = int(input("Enter Consultation ID: "))
        medicine = int(input("Enter Medicine (Inventory) ID: "))
        quantity = int(input("Enter Quantity: "))
        dose = input("Enter Dose : ")
        instruction = input("Enter Instruction : ")
        valid_until = input("Enter Valid Until (YYYY-MM-DD): ")

        query = """
        INSERT INTO medication (
            cons_id, medicine, quantity,
            dose, instruction, valid_until,
            edited_by
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        cur.execute(query, ( cons_id, medicine, quantity,
            dose, instruction, valid_until,
            edited_by))
        med_id=cur.lastrowid
        med_his_id = med_id
        cur.execute("UPDATE medication SET med_his_id=%s WHERE med_id=%s",(med_his_id ,med_id))
        conn.commit()

    except Exception as e:
        print(" Error adding medication:", e)

def view_all_medications():
    try:

        cur.execute("SELECT * FROM medication WHERE medication_is_active='Yes'")
        rows = cur.fetchall()

        if rows:
            headers = [i[0] for i in cur.description]
            print(tabulate(rows, headers=headers, tablefmt="pretty"))
        else:
            print(" No medication records found.")

    except Exception as e:
        print(" Error viewing medications:", e)

def update_medication(edited_by):
    cur.execute("SELECT * FROM medication")
    data = cur.fetchall()
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
    new_version = old_data[10] + 1
    new_data = list(old_data[5:9])

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
                new_value = int(input("Enter updated value : "))
                break
            except ValueError:
                print("Enter only integers.")
    elif choice == 4:
        while True:
            try:
                new_value_input = input("Enter date of birth (YYYY-MM-DD) : ")
                new_value = datetime.strptime(new_value_input, "%Y-%m-%d").date()
                break
            except ValueError:
                print("Invalid date format, use YYYY-MM-DD.")
    else:
        new_value = input("Enter updated value : ")
    new_data[choice-1] = new_value

    cur.execute('''UPDATE medication SET medication_is_active = 'No'
                WHERE med_id = %s''', (med_id,))

    cur.execute('''INSERT INTO medication (med_his_id, quantity, dose, instruction, valid_until, version, edited_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                (med_his_id, *new_data, new_version, edited_by))

    conn.commit()
    print("Medication updated successfully.")


def delete_medication():
    try:

        med_id = int(input("Enter Medication ID to delete: "))
        cur.execute("UPDATE medication SET medication_is_active='No' WHERE med_id = %s", (med_id,))
        conn.commit()

    except Exception as e:
        print(" Error deleting medication:", e)