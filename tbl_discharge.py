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
                FOREIGN KEY (adm_id) REFERENCES tbl_admission (adm_id)
                ''')

except Error as e:
    print(e)