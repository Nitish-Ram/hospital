from mysql.connector import connect, Error
from tabulate import tabulate

try:
    conn = connect(
        host = 'mysql-guyandchair-hospitaldb344.l.aivencloud.com',
        port = '28557',
        user = 'avnadmin',
        password = 'AVNS_kHrKn7uSeIU17qOji3M',
        database = 'defaultdb',
        ssl_ca = 'certs/ca.pem'
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
    cur.execute("""INSERT INTO lookup_code (item_name, item_category, item_if_active, version)
                VALUES
                ('Active', 'patient_status', 'Yes', 0),
                ('Inactive', 'patient_status', 'Yes', 0),
                ('Deceased', 'patient_status', 'Yes', 0),
                ('Clinic_1', 'Location', 'Yes', 0),
                ('Clinic_2', 'Location', 'Yes', 0),
                ('Clinic_3', 'Location', 'Yes', 0),
                ('Credit card', 'Payment_Type', 'Yes', 0),
                ('Insurance', 'Payment_Type', 'Yes', 0),
                ('Cash payment', 'Payment_Type', 'Yes', 0),
                ('Consultation fees', 'Payment_Category', 'Yes', 0),
                ('Lab test charges', 'Payment_Category', 'Yes', 0),
                ('Image test charges', 'Payment_Category', 'Yes', 0),
                ('Medication charges', 'Payment_Category', 'Yes', 0),
                ('Admission charges', 'IP_Payment_Category', 'Yes', 0),
                ('Operation theatre charges', 'IP_Payment_Category', 'Yes', 0),
                ('Procedure charges', 'IP_Payment_Category', 'Yes', 0),
                ('Bed_1', 'Bed', 'Yes', 0),
                ('Bed_2', 'Bed', 'Yes', 0),
                ('Bed_3', 'Bed', 'Yes', 0)""")
    conn.commit()
except Error as e:
    print(e)

def add_items_lookup_code(edited_by):
    while True:
        item_name = input("Enter item name to add : ")
        item_category = input("Enter category of item : ")
        cur.execute("SELECT COUNT(*) FROM lookup_code WHERE item_name=%s AND item_category=%s", (item_name, item_category))
        if cur.fetchone()[0] > 0:
            print("This item already exists in the category.")
            return
        else:
            break
    query = '''INSERT INTO lookup_code (
    item_name, item_category, edited_by
    ) VALUES (%s, %s, %s)
        '''
    cur.execute(query, (item_name, item_category, edited_by))
    item_id = cur.lastrowid
    item_his_id = item_id
    cur.execute('''UPDATE lookup_code SET item_his_id = %s
                WHERE item_id = %s''', (item_his_id, item_id))
    conn.commit()
    print("Item added successfully.")

def update_items_lookup_code(edited_by):
    cur.execute("SELECT * FROM lookup_code")
    data = cur.fetchall()
    valid_ids = [i[0] for i in data]
    headers = [i[0] for i in cur.description]
    print(tabulate(data, headers = headers, tablefmt = 'pretty'))

    while True:
        try:
            item_id = int(input("Enter ID of item to update : "))
            if item_id in valid_ids:
                break
            else:
                print("Item not found. Try again.")
        except ValueError:
            print("Enter only integers.")
    cur.execute('''SELECT * FROM lookup_code where item_id = %s''', (item_id,))
    old_data = cur.fetchone()
    item_his_id = old_data[1]
    new_version = old_data[5] + 1
    new_data = list(old_data[2:4])
    print("Enter value to update.")
    print("1) Item name\n2) Item category")
    while True:
        try:
            choice = int(input("Enter 1 or 2 : "))
            if choice in range(1,3):
                break
            else:
                print("Enter correct value. Try again.")
        except ValueError:
            print("Enter only integers.")
    new_value = input("Enter updated value. : ")
    new_data[choice-1] = new_value
    cur.execute('''UPDATE lookup_code SET item_if_active = 'No'
                WHERE item_id = %s''', (item_id,))
    cur.execute('''INSERT INTO lookup_code (item_his_id, item_name, item_category, version, edited_by) VALUES (%s, %s, %s, %s, %s)''',
                (item_his_id, *new_data, new_version, edited_by))
    conn.commit()
    print("Item updated successfully.")

def remove_items_lookup_code(edited_by):
    cur.execute("SELECT * FROM lookup_code")
    data = cur.fetchall()
    valid_ids = [i[0] for i in data]
    headers = [i[0] for i in cur.description]
    print(tabulate(data, headers = headers, tablefmt = 'pretty'))

    while True:
        try:
            item_id = int(input("Enter ID of item to remove : "))
            if item_id in valid_ids:
                break
            else:
                print("Item not found. Try again.")
        except ValueError:
            print("Enter only integers.")

    cur.execute('SELECT * FROM lookup_code where item_id = %s', (item_id,))
    old_data = cur.fetchone()
    new_version = old_data[5] + 1
    cur.execute('''UPDATE lookup_code SET item_if_active = 'No', version = %s, edited_by = %s
                WHERE item_id = %s''', (new_version, edited_by, item_id))
    conn.commit()
    print("Item removed successfully.")