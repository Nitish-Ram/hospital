from mysql.connector import connect, Error

try:
    conn = connect(
        host = 'localhost',
        user = 'root',
        password = 'test',
        database = 'hospital'
    )
    cur = conn.cursor()
    #lookup_code
    cur.execute('''CREATE TABLE IF NOT EXISTS lookup_code (
                item_id INT AUTO_INCREMENT PRIMARY KEY,
                item_his_id INT,
                item_name VARCHAR(100),
                item_category VARCHAR(100),
                item_if_active ENUM('Yes', 'No') DEFAULT 'Yes',
                version INT DEFAULT 0,
                edited_by INT NULL,
                edited_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
except Error as e:
    print(e)