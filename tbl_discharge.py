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
    cur.execute('''CREATE TABLE IF NOT EXISTS tbl_discharge(
                dis_id INT AUTO_INCREMENT PRIMARY KEY,
                dis_his_id INT,
                adm_id INT,
                discharge_date DATE,
                discharge_medication ENUM('Yes','No') DEFAULT 'No',
                discharge_advice VARCHAR(500),
                followup_date DATE,
                charges_paid ENUM('Yes','No') DEFAULT 'No',
                day_off_cert ENUM ('Yes','No') DEFAULT 'No',
                dis_summary ENUM ('Yes','No') DEFAULT 'No',
                version INT DEFAULT 0,
                edited_by INT NULL,
                edited_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (adm_id) REFERENCES tbl_admission (adm_id)
                )''')

except Error as e:
    print(e)

def record_discharge(edited_by):
    try:
        cur.execute("""
        SELECT a.adm_id, p.patient_name, p.cpr_no, a.adm_date, s.staff_name
        FROM tbl_admission a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN staff s ON a.adm_doctor = s.staff_id
        WHERE a.adm_id NOT IN (SELECT adm_id FROM tbl_discharge WHERE dis_id IS NOT NULL)
        ORDER BY a.adm_date DESC
        """)
        
        admissions = cur.fetchall()
        if not admissions:
            print("No active admissions to discharge.")
            return
        
        print("Active Admissions:")
        headers = [i[0] for i in cur.description]
        print(tabulate(admissions, headers=headers, tablefmt='pretty'))
        
        while True:
            try:
                adm_id = int(input("Enter Admission ID: "))
                if adm_id in [i[0] for i in admissions]:
                    break
                else:
                    print("Invalid admission ID.")
            except ValueError:
                print("Enter only integers.")
        
        while True:
            try:
                discharge_date_input = input("Enter discharge date (YYYY-MM-DD): ")
                discharge_date = datetime.strptime(discharge_date_input, "%Y-%m-%d").date()
                break
            except ValueError:
                print("Invalid date format. Use YYYY-MM-DD.")
        
        discharge_advice = input("Enter discharge advice/notes: ")
        
        while True:
            try:
                followup_input = input("Enter follow-up date (YYYY-MM-DD) or leave blank: ")
                followup_date = datetime.strptime(followup_input, "%Y-%m-%d").date() if followup_input else None
                break
            except ValueError:
                print("Invalid date format. Use YYYY-MM-DD.")
        
        while True:
            discharge_medication = input("Is discharge medication provided (Yes/No): ").lower()
            if discharge_medication in ('yes', 'no'):
                discharge_medication = discharge_medication.capitalize()
                break
            print("Enter only Yes or No.")
        
        while True:
            charges_paid = input("Are all charges paid (Yes/No): ").lower()
            if charges_paid in ('yes', 'no'):
                charges_paid = charges_paid.capitalize()
                break
            print("Enter only Yes or No.")
        
        while True:
            day_off_cert = input("Issue day-off certificate (Yes/No): ").lower()
            if day_off_cert in ('yes', 'no'):
                day_off_cert = day_off_cert.capitalize()
                break
            print("Enter only Yes or No.")
        
        # Insert discharge record
        cur.execute("""
        INSERT INTO tbl_discharge 
        (adm_id, discharge_date, discharge_medication, discharge_advice, followup_date, 
         charges_paid, day_off_cert, dis_summary, edited_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'No', %s)
        """, (adm_id, discharge_date, discharge_medication, discharge_advice, followup_date,
              charges_paid, day_off_cert, edited_by))
        
        dis_id = cur.lastrowid
        cur.execute("UPDATE tbl_discharge SET dis_his_id=%s WHERE dis_id=%s", (dis_id, dis_id))
        
        # Update admission to mark as discharged
        cur.execute("UPDATE tbl_admission SET payment=%s WHERE adm_id=%s", (charges_paid, adm_id))
        
        conn.commit()
        print("Patient discharged successfully.")
        
    except Error as e:
        print(f" Database Error: {e}")

def add_discharge_medication(edited_by):
    """Add/prescribe medication at discharge"""
    try:
        from medication import prescribe_medication
        
        # Get recent discharges
        cur.execute("""
        SELECT d.dis_id, d.adm_id, p.patient_name, d.discharge_date
        FROM tbl_discharge d
        JOIN tbl_admission a ON d.adm_id = a.adm_id
        JOIN patients p ON a.patient_id = p.patient_id
        WHERE d.discharge_medication='No'
        ORDER BY d.discharge_date DESC LIMIT 10
        """)
        
        discharges = cur.fetchall()
        if not discharges:
            print("No pending discharge medication records.")
            return
        
        print("Recent Discharges (pending medication):")
        headers = [i[0] for i in cur.description]
        print(tabulate(discharges, headers=headers, tablefmt='pretty'))
        
        while True:
            try:
                dis_id = int(input("Enter Discharge ID: "))
                if dis_id in [i[0] for i in discharges]:
                    break
                else:
                    print("Invalid discharge ID.")
            except ValueError:
                print("Enter only integers.")
        
        # Get the related consultation to prescribe medication
        cur.execute("""
        SELECT tc.cons_id FROM tbl_consultation tc
        JOIN appointments a ON tc.appt_id = a.appt_id
        JOIN tbl_admission ad ON ad.patient_id = a.patient_id
        WHERE ad.adm_id = (SELECT adm_id FROM tbl_discharge WHERE dis_id=%s)
        ORDER BY tc.cons_date DESC LIMIT 1
        """, (dis_id,))
        
        result = cur.fetchone()
        if result:
            cons_id = result[0]
            # Use existing prescribe_medication function
            prescribe_medication(edited_by)
            
            # Mark discharge medication as added
            cur.execute("UPDATE tbl_discharge SET discharge_medication='Yes' WHERE dis_id=%s", (dis_id,))
            conn.commit()
            print("Discharge medication added successfully.")
        else:
            print("Could not find related consultation.")
        
    except Error as e:
        print(f" Database Error: {e}")

def generate_discharge_summary():
    """Generate discharge summary report"""
    try:
        print(" Discharge Summary Report")
        
        # Get date range
        start_date = input("Enter start date (YYYY-MM-DD): ")
        end_date = input("Enter end date (YYYY-MM-DD): ")
        
        query = """
        SELECT 
            d.dis_id AS ID,
            p.patient_name AS Patient,
            p.cpr_no AS CPR,
            a.adm_date AS Admission_Date,
            d.discharge_date AS Discharge_Date,
            DATEDIFF(d.discharge_date, a.adm_date) AS Days_Admitted,
            d.discharge_medication AS Medication,
            d.charges_paid AS Charges_Paid,
            d.day_off_cert AS Day_Off_Cert,
            s.staff_name AS Treating_Doctor
        FROM tbl_discharge d
        JOIN tbl_admission a ON d.adm_id = a.adm_id
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN staff s ON a.adm_doctor = s.staff_id
        WHERE d.discharge_date BETWEEN %s AND %s
        ORDER BY d.discharge_date DESC
        """
        
        cur.execute(query, (start_date, end_date))
        rows = cur.fetchall()
        
        if rows:
            headers = [i[0] for i in cur.description]
            print(tabulate(rows, headers=headers, tablefmt='pretty'))
            
            # Summary stats
            total_discharges = len(rows)
            avg_stay = sum(row[5] for row in rows) / total_discharges if total_discharges > 0 else 0
            paid_count = sum(1 for row in rows if row[7] == 'Yes')
            
            print(f"\nSummary:")
            print(f"Total Discharges: {total_discharges}")
            print(f"Average Stay (days): {avg_stay:.1f}")
            print(f"Charges Fully Paid: {paid_count}/{total_discharges}")
        else:
            print("No discharge records found for the given date range.")
        
    except Error as e:
        print(f" Database Error: {e}")