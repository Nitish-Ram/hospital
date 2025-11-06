from mysql.connector import connect, Error

try:
    conn = connect(
        host = 'localhost',
        user = 'root',
        password = 'Fawaz@33448113',
        database = 'hospital'
    )
    cur = conn.cursor()
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
except Error as e:
    print(e)