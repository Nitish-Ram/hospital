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
    item_his_id, item_name, item_category, edited_by
    ) VALUES (%s, %s, %s, %s)
        '''
    cur.execute(query, (0, item_name, item_category, edited_by))
    conn.commit()
    print("Item added successfully.")