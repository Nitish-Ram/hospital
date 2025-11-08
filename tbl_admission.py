from mysql.connector import connect, Error

try:
    conn = connect(
        host = 'localhost',
        user = 'root',
        password = 'Fawaz@33448113',
        database = 'hospital'
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
                edited_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
except Error as e:
    print(e)