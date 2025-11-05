from mysql.connector import connect, Error

try:
    conn = connect(
        host = 'localhost',
        user = 'root',
        password = 'test',
        database = 'hospital'
    )
    cur = conn.cursor()
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
except Error as e:
    print(e)