from mysql.connector import connect, Error
from datetime import datetime
from tabulate import tabulate

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
                FOREIGN KEY (procedure_id) REFERENCES lookup_code(item_id)
                )''')
except Error as e:
    print(e)

def add_inpatient_procedure(edited_by, adm_id=None):
    """Add a procedure record for an inpatient"""
    try:
        # Get active admissions if adm_id not provided
        if not adm_id:
            cur.execute("""
            SELECT a.adm_id, p.patient_name, p.cpr_no, a.adm_date, s.staff_name
            FROM tbl_admission a
            JOIN patients p ON a.patient_id = p.patient_id
            JOIN staff s ON a.adm_doctor = s.staff_id
            WHERE a.adm_id NOT IN (
                SELECT adm_id FROM tbl_discharge WHERE dis_id IS NOT NULL
            )
            ORDER BY a.adm_date DESC
            """)
            
            admissions = cur.fetchall()
            if not admissions:
                print("No active admissions.")
                return
            
            print("Active Admissions:")
            headers = [i[0] for i in cur.description]
            print(tabulate(admissions, headers=headers, tablefmt='pretty'))
            
            while True:
                try:
                    adm_id = int(input("Enter admission ID: "))
                    if adm_id in [i[0] for i in admissions]:
                        break
                    else:
                        print("Invalid admission ID.")
                except ValueError:
                    print("Enter only integers.")
        
        # Get procedures from lookup_code
        cur.execute("""
        SELECT item_id, item_name FROM lookup_code 
        WHERE item_category='SurgicalProcedure' AND item_if_active='Yes'
        """)
        
        procedures = cur.fetchall()
        if not procedures:
            print("No procedures available.")
            return
        
        print("\nAvailable Procedures:")
        for proc in procedures:
            print(f"{proc[0]}. {proc[1]}")
        
        while True:
            try:
                procedure_id = int(input("Enter procedure ID: "))
                if procedure_id in [i[0] for i in procedures]:
                    break
                else:
                    print("Invalid procedure ID.")
            except ValueError:
                print("Enter only integers.")
        
        # Get staff members
        cur.execute("SELECT staff_id, staff_name, designation FROM staff WHERE is_active='Yes'")
        staff_list = cur.fetchall()
        
        print("\nAvailable Staff:")
        headers = ['ID', 'Name', 'Designation']
        print(tabulate(staff_list, headers=headers, tablefmt='pretty'))
        
        while True:
            try:
                doctor_id = int(input("Enter doctor's staff ID: "))
                nurse_id = int(input("Enter nurse's staff ID: "))
                if doctor_id in [i[0] for i in staff_list] and nurse_id in [i[0] for i in staff_list]:
                    break
                else:
                    print("Could not find staff IDs. Try again.")
            except ValueError:
                print("Enter only integers.")
        
        while True:
            try:
                date_input = input("Enter date and time (YYYY-MM-DD HH:MM:SS): ")
                date_of_procedure = datetime.strptime(date_input, "%Y-%m-%d %H:%M:%S")
                break
            except ValueError:
                print("Invalid date and time format. Try YYYY-MM-DD HH:MM:SS.")
        
        while True:
            payment_done = input("Payment done (Yes/No): ").lower()
            if payment_done in ('yes', 'no'):
                payment_done = payment_done.capitalize()
                break
            print("Enter only Yes or No.")
        
        while True:
            consumables_paid = input("Consumables paid (Yes/No): ").lower()
            if consumables_paid in ('yes', 'no'):
                consumables_paid = consumables_paid.capitalize()
                break
            print("Enter only Yes or No.")
        
        # Insert procedure record
        cur.execute("""
        INSERT INTO inpatient_procedures 
        (adm_id, procedure_id, date_of_procedure, doctor_id, nurse_id, 
         payment_done, consumables_paid, edited_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (adm_id, procedure_id, date_of_procedure, doctor_id, nurse_id,
              payment_done, consumables_paid, edited_by))
        
        ipp_id = cur.lastrowid
        cur.execute("UPDATE inpatient_procedures SET ipp_his_id=%s WHERE ipp_id=%s", (ipp_id, ipp_id))
        
        conn.commit()
        print("Inpatient procedure recorded successfully.")
        
    except Error as e:
        print(f" Database Error: {e}")

def view_procedures(edited_by=None):
    """View all inpatient procedures"""
    try:
        query = """
        SELECT 
            ip.ipp_id AS ID,
            p.patient_name AS Patient,
            lc.item_name AS Procedure,
            ip.date_of_procedure AS Date,
            s1.staff_name AS Doctor,
            s2.staff_name AS Nurse,
            ip.payment_done AS Payment,
            ip.consumables_paid AS Consumables
        FROM inpatient_procedures ip
        JOIN tbl_admission a ON ip.adm_id = a.adm_id
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN lookup_code lc ON ip.procedure_id = lc.item_id
        JOIN staff s1 ON ip.doctor_id = s1.staff_id
        JOIN staff s2 ON ip.nurse_id = s2.staff_id
        ORDER BY ip.date_of_procedure DESC
        """
        
        cur.execute(query)
        rows = cur.fetchall()
        
        if rows:
            headers = [i[0] for i in cur.description]
            print(tabulate(rows, headers=headers, tablefmt='pretty'))
        else:
            print("No procedures found.")
        
    except Error as e:
        print(f" Database Error: {e}")