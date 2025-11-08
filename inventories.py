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
    cur.execute('''INSERT INTO inventories (inv_name, inv_category, inv_if_active, version)
                VALUES
                ('Paracetamol 200mg', 'Tablet', 'Yes',1),
                ('Paracetamol 500mg', 'Tablet', 'Yes',1),
                ('Brufen 200mg', 'Tablet', 'Yes',1),
                ('Brufen 400mg', 'Tablet', 'Yes',1),
                ('B complex vitamin', 'Tablet', 'Yes',1),
                ('Multivitamin', 'Tablet', 'Yes',1),
                ('B complex', 'Injection', 'Yes',1),
                ('Voveron Pain inj', 'Injection', 'Yes',1),
                ('Paracetamol inj', 'Injection', 'Yes',1),
                ('Voveron Pain inj', 'Injection', 'Yes',1),
                ('Antibiotic inj', 'Injection', 'Yes',1),
                ('Penicillin 500mg', 'Tablet', 'Yes',1),
                ('Azithromycin 250mg', 'Tablet', 'Yes',1),
                ('Saline infusion', 'IV fluid', 'Yes',1),
                ('Dextrose infusion', 'IV fluid', 'Yes',1),
                ('Antibiotic infusion', 'IV fluid', 'Yes',1)
                ''')
except Error as e:
    print(e)