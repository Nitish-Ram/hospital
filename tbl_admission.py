from mysql.connector import connect, Error

try:
    conn = connect(
        host = 'localhost',
        user = 'root',
        password = 'test',
        database = 'hospital'
    )
    cur = conn.cursor()


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
except Error as e:
    print(e)