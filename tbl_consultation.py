from mysql.connector import connect, Error

try:
    conn = connect(
        host = 'localhost',
        user = 'root',
        password = 'test',
        database = 'hospital'
    )
    cur = conn.cursor()

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
except Error as e:
    print(e)