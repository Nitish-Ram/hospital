from mysql.connector import connect, Error

try:
    conn = connect(
        host = 'localhost',
        user = 'root',
        password = 'test',
        database = 'hospital'
    )
    cur = conn.cursor()
    #lookup_code
    cur.execute('''CREATE TABLE IF NOT EXISTS inventories (
                inv_id INT AUTO_INCREMENT PRIMARY KEY, 
                inv_his_id INT,
                inv_name VARCHAR(100),
                inv_category VARCHAR(100),
                inv_if_active ENUM('Yes', 'No') DEFAULT 'Yes',
                version INT DEFAULT 0,
                edited_by INT NULL,
                edited_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS appointments (
                appt_id INT AUTO_INCREMENT PRIMARY KEY,
                appt_his_id INT,
                patient_id INT,
                doctor_id INT,
                clinic INT,
                appt_book_time DATE,
                cons_fee_paid ENUM('Yes','No') DEFAULT 'No',
                cons_payment_receiptno INT,
                cons_paid_amount INT,
                appt_is_active ENUM('Yes','No') DEFAULT 'Yes',
                version INT DEFAULT 0,
                edited_by INT NULL,
                edited_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
                FOREIGN KEY (doctor_id) REFERENCES staff(staff_id),
                FOREIGN KEY (clinic) REFERENCES lookup_code(item_id)
                )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS tbl_consultation(
                cons_id INT AUTO_INCREMENT PRIMARY KEY,
                cons_his_id INT,
                appt_id INT,
                doctor_id INT,
                clinic INT,
                cons_date DATE,
                complaints VARCHAR(500),
                diagnosis VARCHAR(500),
                cons_notes VARCHAR(500),
                lab_test ENUM('Yes','No') DEFAULT 'No',
                imaging_test ENUM('Yes','No') DEFAULT 'No',
                medication ENUM('Yes','No') DEFAULT 'No',
                discharged ENUM('Yes','No') DEFAULT 'No',
                admission_to_ward ENUM('Yes','No') DEFAULT 'No',
                followup_date DATE,
                version INT DEFAULT 0,
                edited_by INT NULL,
                edited_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (appt_id) REFERENCES appointments(appt_id),
                FOREIGN KEY (doctor_id) REFERENCES staff(staff_id),
                FOREIGN KEY (clinic) REFERENCES lookup_code(item_id)
                )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS tbl_admission(
                adm_id INT AUTO_INCREMENT PRIMARY KEY,
                adm_his_id INT,
                patient_id INT,
                adm_date DATE,
                discharge_date DATE,
                discharge_medication ENUM('Yes','No') DEFAULT 'No',
                adm_doctor INT,
                ward INT,
                payment ENUM('Yes','No') DEFAULT 'No',
                version INT DEFAULT 0,
                edited_by INT NULL,
                edited_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS tests (
                test_id INT AUTO_INCREMENT PRIMARY KEY,
                test_his_id INT,
                cons_id INT,
                test_name INT,
                fees_paid ENUM('Yes','No') DEFAULT 'No',
                paid_amt VARCHAR(50),
                payment_date DATE,
                receipt_no INT,
                test_result VARCHAR(250),
                version INT DEFAULT 0,
                edited_by INT NULL,
                edited_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cons_id) REFERENCES tbl_consultation(cons_id),
                FOREIGN KEY (test_name) REFERENCES lookup_code(item_id)
                )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS inpatient_procedures (
                ipp_id INT AUTO_INCREMENT PRIMARY KEY,
                ipp_his_id INT,
                adm_id INT,
                procedure_id INT,
                date_of_procedure DATE,
                doctor_id INT,
                nurse_id INT,
                payment_done ENUM('Yes','No') DEFAULT 'No',
                consumables_paid ENUM('Yes','No') DEFAULT 'No',
                version INT DEFAULT 0,
                edited_by INT NULL,
                edited_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (adm_id) REFERENCES tbl_admission(adm_id),
                FOREIGN KEY (doctor_id) REFERENCES staff(staff_id),
                FOREIGN KEY (nurse_id) REFERENCES staff(staff_id)
                )''')
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