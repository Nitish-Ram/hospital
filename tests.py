from mysql.connector import connect, Error
from tabulate import tabulate

def createtable_tests():
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
                    cons_id INT,
                    adm_id INT,
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
    except Error as e:
        print(e)

def add_test(edited_by):
    try:
        #for now
        cons_id = input("Enter Consultation ID: ")
        test_name = input("Enter Test Name : ")
        fees_paid = input("Fees Paid (Yes/No): ")
        paid_amt = input("Enter Paid Amount: ")
        payment_date = input("Enter Payment Date (YYYY-MM-DD): ")
        receipt_no = input("Enter Receipt No: ")
        test_result = input("Enter Test Result: ") 

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

def view_tests():
    try:
        while True:
            ch=input("enter choice 1.search test 2.view all tests")
            if ch=='1':
                test_id = input("Enter Test ID: ")
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

        old_data=cur.fetchone()
        new_data=list(old_data[1:-2])
        new_data[-1]+=1 #version update

        while True:
            ch=input("enter choice (1.update test result 2.payment update")
            if ch=='1':
                new_result = input("Enter New Test Result: ")
                new_data[-3]=new_result
            elif ch=='2':
                paid_amt = input("Enter Paid Amount: ")
                payment_date = input("Enter Payment Date (YYYY-MM-DD): ")
                receipt_no = input("Enter Receipt Number: ")
                new_data[5],new_data[6],new_data[7]=paid_amt,payment_date,receipt_no
            else:
                print("invalid input")
                continue
            break
        
        cur.execute('''
        INSERT INTO tests 
        (test_his_id,cons_id, test_name, fees_paid, paid_amt, payment_date, receipt_no, test_result, test_is_active, version, edited_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',(*new_data,edited_by))

        cur.execute("UPDATE tests SET test_is_active='No' WHERE test_id=%s",(test_id,))
        conn.commit()

    except Error as e:
        print(f" Database Error: {e}")

def delete_test():
    #there is no set active
    try:
        test_id = input("Enter Test ID: ")

        cur.execute("UPDATE tests SET test_is_active='No' WHERE test_id=%s",(test_id,))
        conn.commit()

    except Error as e:
        print(f"Database Error: {e}")
