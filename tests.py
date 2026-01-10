from mysql.connector import connect, Error
from tabulate import tabulate
from datetime import datetime

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

    cur.execute('''CREATE TABLE IF NOT EXISTS tests (
                test_id INT AUTO_INCREMENT PRIMARY KEY,
                test_his_id INT,
                cons_id INT NULL,
                adm_id INT NULL,
                test_name INT,
                fees_paid ENUM('Yes','No') DEFAULT 'No',
                paid_amt VARCHAR(50),
                payment_date DATE,
                receipt_no INT,
                test_result VARCHAR(250),
                test_is_active ENUM('Yes','No') DEFAULT 'Yes',
                version INT DEFAULT 0,
                edited_by INT NULL,
                edited_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cons_id) REFERENCES tbl_consultation(cons_id),
                FOREIGN KEY (test_name) REFERENCES lookup_code(item_id),
                FOREIGN KEY (adm_id) REFERENCES tbl_admission(adm_id)
                )''')
    
    conn.commit()

except Error as e:
    print(e)

def add_test_cons(edited_by, cons_id):
    try:
        test_name_text = input("Enter Test Name: ")
        cur.execute("SELECT item_id FROM lookup_code WHERE item_name=%s", (test_name_text,))
        names = cur.fetchone()
        if not names:
            print("Test not found!")
            return
        test_name = names[0]
        fees_paid = input("Fees Paid (Yes/No) : ")
        paid_amt = input("Enter Paid Amount : ")
        while True:
            payment_date = input("Enter Payment Date (YYYY-MM-DD): ")
            try:
                datetime.strptime(payment_date, "%Y-%m-%d")
                break
            except ValueError:
                print("Invalid date format. Use YYYY-MM-DD.")
        receipt_no = input("Enter Receipt No : ")
        test_result = input("Enter Test Result : ") 

        query = '''
        INSERT INTO tests 
        (cons_id, test_name, fees_paid, paid_amt, payment_date, receipt_no, test_result, edited_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        '''
        cur.execute(query, (cons_id, test_name, fees_paid, paid_amt, payment_date, receipt_no, test_result, edited_by))
        test_id=cur.lastrowid
        cur.execute("UPDATE tests SET test_his_id=%s where test_id=%s",(test_id,test_id))
        conn.commit()

        print("Test record added successfully!")

    except Error as e:
        print(f" Database Error: {e}")
def add_test_adm(edited_by, adm_id):
    try:
        test_name_text = input("Enter Test Name: ")
        cur.execute("SELECT item_id FROM lookup_code WHERE item_name=%s", (test_name_text,))
        names = cur.fetchone()
        if not names:
            print("Test not found!")
            return
        test_name = names[0]
        fees_paid = input("Fees Paid (Yes/No) : ")
        paid_amt = input("Enter Paid Amount : ")
        while True:
            payment_date = input("Enter Payment Date (YYYY-MM-DD) : ")
            try:
                datetime.strptime(payment_date, "%Y-%m-%d")
                break
            except ValueError:
                print("Invalid date format. Use YYYY-MM-DD.")
        receipt_no = input("Enter Receipt No : ")
        test_result = input("Enter Test Result : ") 
        query = '''
        INSERT INTO tests 
        (adm_id, test_name, fees_paid, paid_amt, payment_date, receipt_no, test_result, edited_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        '''
        cur.execute(query, (adm_id, test_name, fees_paid, paid_amt, payment_date, receipt_no, test_result, edited_by))
        test_id=cur.lastrowid
        cur.execute("UPDATE tests SET test_his_id=%s where test_id=%s",(test_id,test_id))
        conn.commit()

        print("Test record added successfully!")

    except Error as e:
        print(f" Database Error: {e}")

def view_tests():
    try:
        while True:
            ch=input("Enter choice 1.Search test 2.View all tests\n>")
            if ch=='1':
                test_id = input("Enter Test ID: ")
                if not test_id.isdigit():
                    print("Invalid Test ID. Must be a number.")
                    continue
                cur.execute('''
                SELECT test_id, cons_id, test_name, fees_paid, paid_amt, payment_date,receipt_no, test_result
                FROM tests WHERE test_is_active='Yes' AND test_id=%s
                ''',(test_id,))
            
            elif ch=='2':
                cur.execute('''
                SELECT test_id, cons_id, test_name, fees_paid, paid_amt, payment_date,receipt_no, test_result
                FROM tests WHERE test_is_active='Yes' ORDER BY payment_date DESC
                ''')
            else:
                print("invalid choice")
                continue
            break
        rows = cur.fetchall()
        header=[i[0] for i in cur.description]
        if rows:
            print(tabulate(rows, headers=header, tablefmt="pretty"))
        else:
            print("No test records found.")

    except Error as e:
        print(f" Database Error: {e}")

def update_test(edited_by):
    try:
        test_id = input("Enter Test ID: ")
        cur.execute("SELECT * FROM tests WHERE test_id=%s AND test_is_active='Yes'",(test_id,))

        old_data = cur.fetchone()
        new_data = list(old_data[1:-2])
        new_data[-1] += 1


        while True:
            ch=input("Enter choice 1. Update test result 2. Payment update : ")
            if ch=='1':
                new_result = input("Enter New Test Result: ")
                new_data[8]=new_result
            elif ch=='2':
                paid_amt = input("Enter Paid Amount: ")
                while True:
                    payment_date = input("Enter Payment Date (YYYY-MM-DD): ")
                    try:
                        datetime.strptime(payment_date, "%Y-%m-%d")
                        break
                    except ValueError:
                        print("Invalid date format. Use YYYY-MM-DD.")
                receipt_no = input("Enter Receipt Number: ")
                new_data[5],new_data[6],new_data[7]=paid_amt,payment_date,receipt_no
            else:
                print("invalid input")
                continue
            break
        
        cur.execute('''
        INSERT INTO tests 
        (test_his_id,cons_id, adm_id, test_name, fees_paid, paid_amt, payment_date, receipt_no, test_result, test_is_active, version, edited_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',(*new_data,edited_by))

        cur.execute("UPDATE tests SET test_is_active='No' WHERE test_id=%s",(test_id,))
        conn.commit()

    except Error as e:
        print(f" Database Error: {e}")

def delete_test():
    try:
        test_id = input("Enter Test ID: ")
        cur.execute("UPDATE tests SET test_is_active='No' WHERE test_id=%s",(test_id,))
        conn.commit()
    except Error as e:
        print(f"Database Error: {e}")