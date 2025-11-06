from mysql.connector import connect, Error

try:
    conn = connect(
        host = 'localhost',
        user = 'root',
        password = 'Fawaz@33448113',
        database = 'hospital'
    )
    cur = conn.cursor()

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
except Error as e:
    print(e)