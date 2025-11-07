from mysql.connector import connect, Error
from tabulate import tabulate

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
                FOREIGN KEY (cons_id) REFERENCES tbl_consultation(cons_id)
                )''')
except Error as e:
    print(e)

def add_medication(edited_by):
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
        cur.execute("UPDATE medication SET med_his_id=%s WHERE med_id=%s",(med_id,med_id))
        
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

def search_medication_by_consultation():
    try:

        cons_id = int(input("Enter Consultation ID to search medications: "))
        cur.execute("SELECT * FROM medication WHERE cons_id = %s AND medication_is_active='Yes'", (cons_id,))
        rows = cur.fetchall()

        if rows:
            headers = [i[0] for i in cur.description]
            print(tabulate(rows, headers=headers, tablefmt="pretty"))
        else:
            print("No medications found for this consultation.")

    except Exception as e:
        print(" Error searching medication:", e)

def update_medication(edited_by):
    try:

        med_id = int(input("Enter Medication ID to update: "))
        cur.execute("SELECT * FROM medication WHERE med_id=%s",(med_id,))
        old_data=cur.fetchone()
        cur.execute("UPDATE medication SET medication_is_active='No' WHERE med_id = %s", (med_id,))

        print("Leave field blank if no change is needed.")
        dose = input("New Dose: ")
        instruction = input("New Instruction: ")
        valid_until = input("New Valid Until (YYYY-MM-DD): ")

        new_data=list(old_data[1:-2])
        new_data[-1]+=1
        new_data[-5],new_data[-4],new_data[-3]=dose,instruction,valid_until

        query = """
        INSERT INTO medication (
            med_his_id, cons_id, medicine, quantity,
            dose, instruction, valid_until,medication_is_active,
            version,edited_by
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cur.execute(query, ( *new_data, edited_by))

        conn.commit()

        print(" Medication updated successfully!")

    except Exception as e:
        print(" Error updating medication:", e)

def delete_medication():
    try:

        med_id = int(input("Enter Medication ID to delete: "))
        cur.execute("UPDATE medication SET medication_is_active='No' WHERE med_id = %s", (med_id,))
        conn.commit()

    except Exception as e:
        print(" Error deleting medication:", e)