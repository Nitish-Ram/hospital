from mysql.connector import connect, Error

try:
    conn = connect(
        host = 'localhost',
        user = 'root',
        password = 'Fawaz@33448113',
        database = 'hospital'
    )
    cur = conn.cursor()

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

