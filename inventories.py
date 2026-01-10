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
    
    conn.commit()

except Error as e:
    print(e)

def add_inventory(edited_by):
    try:
        inv_name = input("Enter Inventory Item Name: ")
        inv_category = input("Enter Category : ")
        query = """
        INSERT INTO inventories (inv_name, inv_category, edited_by)
        VALUES (%s, %s, %s)
        """
        cur.execute(query, ( inv_name, inv_category, edited_by))
        inv_id=cur.lastrowid
        inv_his_id = inv_id
        cur.execute("UPDATE inventories SET inv_his_id=%s WHERE inv_id=%s",(inv_his_id, inv_id))
        conn.commit()
        print(" Inventory item added successfully!")

    except Exception as e:
        print(" Error adding inventory:", e)

def view_all_inventories():
    try:    
        cur.execute("SELECT * FROM inventories WHERE inv_if_active='Yes'")
        rows = cur.fetchall()
        if rows:
            headers = [i[0] for i in cur.description]
            print(tabulate(rows, headers=headers, tablefmt="pretty"))
        else:
            print(" No inventory items found.")
    except Exception as e:
        print(" Error viewing inventories:", e)

def update_inventory(edited_by):
    try:
        cur.execute("SELECT * FROM inventories")
        data = cur.fetchall()
        valid_ids = [i[0] for i in data]
        headers = [i[0] for i in cur.description]
        print(tabulate(data, headers=headers, tablefmt='pretty'))

        while True:
            inv_id = int(input("Enter Inventory ID to update: "))
            if inv_id not in valid_ids:
                print('not found')
            else:break
        
        cur.execute("SELECT * FROM inventories WHERE inv_id=%s",(inv_id,))
        old_data=cur.fetchone()
        new_data=list(old_data[1:-2])
        new_data[-1] += 1

        while True:
            choice = input("Field to be updated (1.name,2.category,3.both): ")
            if choice == '1':
                inv_name = input("New Item Name: ")
                new_data[1]=inv_name
            elif choice == '2':
                inv_category = input("New Category: ")
                new_data[2]=inv_category
            elif choice=='3':
                inv_name = input("New Item Name: ")
                inv_category = input("New Category: ")
                new_data[1],new_data[2]=inv_name,inv_category
            else:
                print("enter a valid choice")
                continue
            break
        
        cur.execute("UPDATE inventories SET inv_if_active='No' WHERE inv_id = %s", (inv_id,))

        cur.execute('''INSERT INTO inventories (inv_his_id,inv_name, inv_category,inv_if_active,version, edited_by)
                    VALUES (%s,%s,%s,%s,%s,%s)''',
                    (*new_data,edited_by))

        conn.commit()

        print(" Inventory updated successfully!")
    except Exception as e:
        print("Error updating inventory:", e)

def delete_inventory(edited_by):
    try:
        inv_id = int(input("Enter Inventory ID to delete: "))
        cur.execute("UPDATE inventories SET inv_if_active='No', edited_by = %s WHERE inv_id = %s", (edited_by, inv_id))
        conn.commit()
        print("Inventory item deleted successfully.")

    except Exception as e:
        print(" Error deleting inventory:", e)