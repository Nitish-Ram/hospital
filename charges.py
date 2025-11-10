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

    cur.execute('''CREATE TABLE IF NOT EXISTS charges (
                charge_id INT AUTO_INCREMENT PRIMARY KEY,
                charge_his_id INT,
                cons_id INT NULL,
                adm_id INT NULL,
                payment_category INT,
                payment_date DATE,
                item_quantity INT,
                payment_type INT,
                payment_note VARCHAR(250),
                paid_amt VARCHAR(100),
                charge_status INT,
                version INT DEFAULT 0,
                edited_by INT NULL,
                edited_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cons_id) REFERENCES tbl_consultation(cons_id),
                FOREIGN KEY (payment_category) REFERENCES lookup_code(item_id),
                FOREIGN KEY (payment_type) REFERENCES lookup_code(item_id),
                FOREIGN KEY (charge_status) REFERENCES lookup_code(item_id)
                )''')
                #status ENUM('','Paid', 'Refunded', 'Cancelled') DEFAULT '')
except Error as e:
    print(e)

def add_charge(edited_by):
    try:
        cons_id = input("Enter Consultation ID : ")
        adm_id = input("Enter Admission ID : ") 
        payment_category = input("Enter Payment Category : ")
        payment_date = input("Enter Payment Date : ")
        item_quantity = input("Enter Quantity: ")
        payment_type = input("Enter Payment Type : ")
        payment_note = input("Enter Payment Note: ")
        paid_amt = input("Enter Paid Amount: ")
        charge_status = input("Enter Charge Status : ")

        query = """
        INSERT INTO charges
        (cons_id, adm_id, payment_category, payment_date, item_quantity,
         payment_type, payment_note, paid_amt, charge_status,edited_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(query, (
            cons_id, adm_id, payment_category, payment_date, item_quantity,
            payment_type, payment_note, paid_amt, charge_status,edited_by
        ))

        charge_his_id=cur.lastrowid
        cur.execute("UPDATE charges set charge_his_id=%s WHERE charge_id=%s",(charge_his_id,charge_his_id))
        
        conn.commit()
        print(" Charge added successfully!")

    except Error as e:
        print(f" Database Error: {e}")

def view_charges():
    try:
        query = """
        SELECT 
            c.charge_id AS ID,
            p.patient_name AS Patient,
            s.staff_name AS Doctor,
            lc1.item_name AS Payment_Category,
            c.payment_date AS Date,
            c.item_quantity AS Qty,
            lc2.item_name AS Payment_Type,
            c.paid_amt AS Amount,
            lc3.item_name AS Status
        FROM charges c
        LEFT JOIN patients p ON a.patient_id = p.patient_id
        LEFT JOIN staff s ON t.doctor_id = s.staff_id
        LEFT JOIN lookup_code lc1 ON c.payment_category = lc1.item_id
        LEFT JOIN lookup_code lc2 ON c.payment_type = lc2.item_id
        LEFT JOIN lookup_code lc3 ON c.charge_status = lc3.item_id
        ORDER BY c.payment_date DESC
        """

        cur.execute(query)
        rows = cur.fetchall()
        header=[i[0] for i in cur.description ]

        if rows:
            print(tabulate(rows, headers=header, tablefmt="pretty"))
        else:
            print("No charges found.")

    except Error as e:
            print(f" Database Error: {e}")

def update_charge_status(edited_by):
    try:
        
        charge_id = input("Enter Charge ID: ")
        cur.execute("SELECT * FROM charges WHERE charge_id=%s",(charge_id,))
        old_data=cur.fetchone()
        new_data=list(old_data[1:-2])
        new_data[-1]+=1 # version update

        while True:
            ch=input("what to change?(1-5)")
            if ch=='1':
                payment_category = input("Enter Payment Category : ")
                new_data[3]=payment_category
            elif ch=='2':
                payment_date = input("Enter Payment Date : ")
                new_data[4]=payment_date
            elif ch=='3':
                item_quantity = input("Enter Quantity: ")
                new_data[5]=item_quantity
            elif ch=='4':
                payment_type = input("Enter Payment Type : ")
                new_data[6]=payment_type
            elif ch=='5':
                payment_note = input("Enter Payment Note: ")
                new_data[7]=payment_note
            else:
                print("invalid input")
                continue
            break

        cur.execute("""
        INSERT INTO charges
        (charge_his_id,cons_id, adm_id, payment_category, payment_date, item_quantity,
         payment_type, payment_note, paid_amt, charge_status,version,edited_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s ,%s ,%s)
        """,(*new_data,edited_by))

    except Error as e:
        print(f" Database Error: {e}")

def delete_charge():
    try:
        #u dint add things in table so idk man
        charge_id = input("Enter Charge ID: ")

        cur.execute("DELETE FROM charges WHERE charge_id = %s", (charge_id,))
        conn.commit()

    except Error as e:
        print(f" Database Error: {e}")