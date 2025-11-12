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


    cur.execute('''CREATE TABLE IF NOT EXISTS tbl_admission(
                adm_id INT AUTO_INCREMENT PRIMARY KEY,
                adm_his_id INT,
                patient_id INT,
                adm_date DATE,
                adm_doctor INT,
                ward INT,
                payment ENUM('Yes','No') DEFAULT 'No',
                version INT DEFAULT 0,
                edited_by INT NULL,
                edited_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
                FOREIGN KEY (adm_doctor) REFERENCES staff(staff_id),
                FOREIGN KEY (ward) REFERENCES lookup_code(item_id)
                )''')
except Error as e:
    print(e)

def add_admission(edited_by):
    """Admit a patient to the hospital"""
    try:
        # Get patients (preferably from recent consultations)
        cur.execute("""
        SELECT DISTINCT p.patient_id, p.patient_name, p.cpr_no, s.staff_name
        FROM patients p
        LEFT JOIN appointments a ON p.patient_id = a.patient_id
        LEFT JOIN tbl_consultation tc ON a.appt_id = tc.appt_id
        LEFT JOIN staff s ON tc.doctor_id = s.staff_id
        WHERE p.is_active = 'Yes'
        ORDER BY p.patient_id DESC LIMIT 20
        """)
        
        patients = cur.fetchall()
        if not patients:
            print("No patients available.")
            return
        
        print("Recent Patients:")
        headers = [i[0] for i in cur.description]
        print(tabulate(patients, headers=headers, tablefmt='pretty'))
        
        while True:
            try:
                patient_id = int(input("Enter patient ID: "))
                if patient_id in [i[0] for i in patients]:
                    break
                else:
                    print("Invalid patient ID.")
            except ValueError:
                print("Enter only integers.")
        
        # Get admitting doctor
        cur.execute("""
        SELECT staff_id, staff_name FROM staff 
        WHERE is_active='Yes' AND (designation LIKE '%Doctor%' OR designation LIKE '%Consultant%')
        """)
        
        doctors = cur.fetchall()
        print("\nAvailable Doctors:")
        for doc in doctors:
            print(f"{doc[0]}. {doc[1]}")
        
        while True:
            try:
                adm_doctor = int(input("Enter admitting doctor's staff ID: "))
                if adm_doctor in [i[0] for i in doctors]:
                    break
                else:
                    print("Invalid doctor ID.")
            except ValueError:
                print("Enter only integers.")
        
        # Get ward
        cur.execute("""
        SELECT item_id, item_name FROM lookup_code 
        WHERE item_category='Ward' AND item_if_active='Yes'
        """)
        
        wards = cur.fetchall()
        if not wards:
            print("No wards available.")
            return
        
        print("\nAvailable Wards:")
        for ward in wards:
            print(f"{ward[0]}. {ward[1]}")
        
        while True:
            try:
                ward = int(input("Enter ward ID: "))
                if ward in [i[0] for i in wards]:
                    break
                else:
                    print("Invalid ward ID.")
            except ValueError:
                print("Enter only integers.")
        
        while True:
            try:
                adm_date_input = input("Enter admission date (YYYY-MM-DD): ")
                adm_date = datetime.strptime(adm_date_input, "%Y-%m-%d").date()
                break
            except ValueError:
                print("Invalid date format. Use YYYY-MM-DD.")
        
        # Insert admission record
        cur.execute("""
        INSERT INTO tbl_admission 
        (patient_id, adm_date, adm_doctor, ward, edited_by)
        VALUES (%s, %s, %s, %s, %s)
        """, (patient_id, adm_date, adm_doctor, ward, edited_by))
        
        adm_id = cur.lastrowid
        cur.execute("UPDATE tbl_admission SET adm_his_id=%s WHERE adm_id=%s", (adm_id, adm_id))
        
        conn.commit()
        print(f"Patient admitted successfully. Admission ID: {adm_id}")
        
    except Error as e:
        print(f" Database Error: {e}")

def view_admissions(edited_by=None):
    """View all active admissions"""
    try:
        query = """
        SELECT 
            a.adm_id AS ID,
            p.patient_name AS Patient,
            p.cpr_no AS CPR,
            a.adm_date AS Admission_Date,
            s.staff_name AS Doctor,
            lc.item_name AS Ward,
            a.payment AS Payment_Status,
            a.version AS Version
        FROM tbl_admission a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN staff s ON a.adm_doctor = s.staff_id
        JOIN lookup_code lc ON a.ward = lc.item_id
        WHERE a.adm_id NOT IN (
            SELECT adm_id FROM tbl_discharge WHERE dis_id IS NOT NULL
        )
        ORDER BY a.adm_date DESC
        """
        
        cur.execute(query)
        rows = cur.fetchall()
        
        if rows:
            headers = [i[0] for i in cur.description]
            print(tabulate(rows, headers=headers, tablefmt='pretty'))
            print(f"\nTotal Active Admissions: {len(rows)}")
        else:
            print("No active admissions.")
        
    except Error as e:
        print(f" Database Error: {e}")

def update_admission(edited_by):
    """Update admission details (doctor, ward, payment status)"""
    try:
        # Get active admissions
        cur.execute("""
        SELECT a.adm_id, p.patient_name, p.cpr_no, s.staff_name, lc.item_name
        FROM tbl_admission a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN staff s ON a.adm_doctor = s.staff_id
        JOIN lookup_code lc ON a.ward = lc.item_id
        WHERE a.adm_id NOT IN (
            SELECT adm_id FROM tbl_discharge WHERE dis_id IS NOT NULL
        )
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
                adm_id = int(input("Enter admission ID to update: "))
                if adm_id in [i[0] for i in admissions]:
                    break
                else:
                    print("Invalid admission ID.")
            except ValueError:
                print("Enter only integers.")
        
        # Get current admission data
        cur.execute("SELECT * FROM tbl_admission WHERE adm_id=%s", (adm_id,))
        old_data = cur.fetchone()
        adm_his_id = old_data[1]
        new_version = old_data[7] + 1
        
        print("\nWhat do you want to update?")
        print("1. Doctor")
        print("2. Ward")
        print("3. Payment Status")
        
        while True:
            choice = input("Enter choice (1-3): ").strip()
            if choice in ('1', '2', '3'):
                break
            print("Invalid choice.")
        
        new_data = list(old_data[1:7])
        
        if choice == '1':
            # Change doctor
            cur.execute("""
            SELECT staff_id, staff_name FROM staff 
            WHERE is_active='Yes' AND (designation LIKE '%Doctor%' OR designation LIKE '%Consultant%')
            """)
            
            doctors = cur.fetchall()
            print("Available Doctors:")
            for doc in doctors:
                print(f"{doc[0]}. {doc[1]}")
            
            while True:
                try:
                    new_doctor = int(input("Enter new doctor ID: "))
                    if new_doctor in [i[0] for i in doctors]:
                        new_data[3] = new_doctor
                        break
                    else:
                        print("Invalid doctor ID.")
                except ValueError:
                    print("Enter only integers.")
        
        elif choice == '2':
            # Change ward
            cur.execute("""
            SELECT item_id, item_name FROM lookup_code 
            WHERE item_category='Ward' AND item_if_active='Yes'
            """)
            
            wards = cur.fetchall()
            print("Available Wards:")
            for ward in wards:
                print(f"{ward[0]}. {ward[1]}")
            
            while True:
                try:
                    new_ward = int(input("Enter new ward ID: "))
                    if new_ward in [i[0] for i in wards]:
                        new_data[4] = new_ward
                        break
                    else:
                        print("Invalid ward ID.")
                except ValueError:
                    print("Enter only integers.")
        
        elif choice == '3':
            # Change payment status
            while True:
                payment_status = input("Payment status (Yes/No): ").lower()
                if payment_status in ('yes', 'no'):
                    new_data[5] = payment_status.capitalize()
                    break
                print("Enter only Yes or No.")
        
        # Insert new version record
        cur.execute("""
        INSERT INTO tbl_admission 
        (adm_his_id, patient_id, adm_date, adm_doctor, ward, payment, version, edited_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (adm_his_id, *new_data, new_version, edited_by))
        
        conn.commit()
        print("Admission record updated successfully.")
        
    except Error as e:
        print(f" Database Error: {e}")

def get_patient_admissions(patient_id, edited_by=None):
    """Get all admissions for a specific patient"""
    try:
        query = """
        SELECT 
            a.adm_id AS ID,
            a.adm_date AS Admission_Date,
            CASE 
                WHEN d.dis_id IS NOT NULL THEN d.discharge_date 
                ELSE 'Active' 
            END AS Discharge_Date,
            s.staff_name AS Doctor,
            lc.item_name AS Ward,
            a.payment AS Payment
        FROM tbl_admission a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN staff s ON a.adm_doctor = s.staff_id
        JOIN lookup_code lc ON a.ward = lc.item_id
        LEFT JOIN tbl_discharge d ON a.adm_id = d.adm_id
        WHERE p.patient_id = %s
        ORDER BY a.adm_date DESC
        """
        
        cur.execute(query, (patient_id,))
        rows = cur.fetchall()
        
        if rows:
            headers = [i[0] for i in cur.description]
            print(f"\nAdmission History for Patient ID {patient_id}:")
            print(tabulate(rows, headers=headers, tablefmt='pretty'))
        else:
            print(f"No admissions found for patient ID {patient_id}.")
        
    except Error as e:
        print(f" Database Error: {e}")