from mysql.connector import connect, Error

try:
    conn = connect(
        host = 'localhost',
        user = 'root',
        password = 'Fawaz@33448113',
        database = 'hospital'
    )
    cur = conn.cursor()

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
except Error as e:
    print(e)