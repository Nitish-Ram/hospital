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
    
    conn.commit()

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
        LEFT JOIN tbl_consultation tc ON c.cons_id = tc.cons_id
        LEFT JOIN appointments a ON tc.appt_id = a.appt_id
        LEFT JOIN patients p ON a.patient_id = p.patient_id
        LEFT JOIN staff s ON tc.doctor_id = s.staff_id
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
        if not old_data:
            print("Charge not found.")
            return
        new_data=list(old_data[1:-2])
        new_data[-1]+=1

        while True:
            ch=input("Enter category to change 1.Payment category, 2.Date, 3.Quantity, 4.Payment type, 5.Notes : ")
            if ch=='1':
                payment_category = input("Enter Payment Category : ")
                new_data[3]=payment_category
            elif ch=='2':
                while True:
                    payment_date = input("Enter Valid Until (YYYY-MM-DD): ")
                    try:
                        datetime.strptime(payment_date, "%Y-%m-%d")
                        break
                    except ValueError:
                        print("Invalid date format. Enter in YYYY-MM-DD format.")
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
        UPDATE charges SET charge_his_id=%s, cons_id=%s, adm_id=%s, payment_category=%s, payment_date=%s, item_quantity=%s,
         payment_type=%s, payment_note=%s, paid_amt=%s, charge_status=%s, version=%s, edited_by=%s
        WHERE charge_id=%s
        """,(*new_data, edited_by, int(charge_id)))
        conn.commit()
        print("Charge updated successfully.")

    except Error as e:
        print(f" Database Error: {e}")

def get_unpaid_charges(edited_by=None):
    """View all unpaid charges for patients"""
    try:
        query = """
        SELECT 
            c.charge_id AS ID,
            p.patient_name AS Patient,
            p.cpr_no AS CPR,
            lc1.item_name AS Category,
            c.payment_date AS Date,
            c.paid_amt AS Amount,
            lc3.item_name AS Status
        FROM charges c
        LEFT JOIN tbl_consultation tc ON c.cons_id = tc.cons_id
        LEFT JOIN appointments a ON tc.appt_id = a.appt_id
        LEFT JOIN patients p ON a.patient_id = p.patient_id
        LEFT JOIN lookup_code lc1 ON c.payment_category = lc1.item_id
        LEFT JOIN lookup_code lc3 ON c.charge_status = lc3.item_id
        WHERE lc3.item_name != 'Paid' OR c.charge_status NOT IN (
            SELECT item_id FROM lookup_code WHERE item_name = 'Paid'
        )
        ORDER BY c.payment_date DESC
        """
        
        cur.execute(query)
        rows = cur.fetchall()
        header=[i[0] for i in cur.description]
        
        if rows:
            print(tabulate(rows, headers=header, tablefmt="pretty"))
            total_unpaid = sum(float(row[5]) if row[5] else 0 for row in rows)
            print(f"\nTotal Unpaid Amount: {total_unpaid:.2f}")
        else:
            print("No unpaid charges found.")
            
    except Error as e:
        print(f" Database Error: {e}")

def record_payment(edited_by):
    """Record payment for a charge"""
    try:
        charge_id = input("Enter Charge ID to mark as paid: ")
        
        cur.execute("SELECT * FROM charges WHERE charge_id=%s",(charge_id,))
        charge_data = cur.fetchone()
        
        if not charge_data:
            print("Charge not found.")
            return
        
        cur.execute("SELECT item_id FROM lookup_code WHERE item_name='Paid' AND item_category='charge_status'")
        paid_status = cur.fetchone()
        
        if not paid_status:
            print("Paid status not found in lookup_code. Please ensure it exists.")
            return
        
        paid_status_id = paid_status[0]
        payment_date = input("Enter payment date (YYYY-MM-DD): ")
        paid_amount = input("Enter payment amount: ")
        receipt_no = input("Enter receipt number (optional): ")
        
        charge_his_id = charge_data[1]
        new_version = charge_data[11] + 1
        
        cur.execute("""
        INSERT INTO charges 
        (charge_his_id, cons_id, adm_id, payment_category, payment_date, item_quantity,
         payment_type, payment_note, paid_amt, charge_status, version, edited_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (charge_his_id, charge_data[2], charge_data[3], charge_data[4], payment_date, charge_data[6],
              charge_data[7], charge_data[8], paid_amount, paid_status_id, new_version, edited_by))
        
        cur.execute("UPDATE charges SET charge_status=%s WHERE charge_id=%s", (paid_status_id, int(charge_id)))
        
        conn.commit()
        print(f"Payment recorded successfully. Amount: {paid_amount}, Receipt: {receipt_no if receipt_no else 'N/A'}")
        
    except Error as e:
        print(f" Database Error: {e}")