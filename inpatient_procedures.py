from mysql.connector import connect, Error

try:
    conn = connect(
        host = 'localhost',
        user = 'root',
        password = 'Fawaz@33448113',
        database = 'hospital'
    )
    cur = conn.cursor()

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
except Error as e:
    print(e)