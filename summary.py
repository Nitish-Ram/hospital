from mysql.connector import connect, Error
from tabulate import tabulate

try:
    conn = connect(
        host = 'localhost',
        user = 'root',
        password = 'Fawaz@33448113',
        database = 'hospital'
    )
    cur = conn.cursor()

except Error as e:
    print(e)

def total_revenue_summary():
    try:

        cur.execute('''
        SELECT DATE(c.payment_date) AS Date,
        COUNT(*) AS Total_Transactions,
        SUM(CAST(c.paid_amt AS DECIMAL(10,2))) AS Total_Revenue
        FROM charges c WHERE c.payment_date IS NOT NULL
        GROUP BY DATE(c.payment_date)
        ORDER BY Date DESC
        ''')

        rows = cur.fetchall()
        header=[i[0] for i in cur.description]
        if rows:
            print(tabulate(rows, headers=header, tablefmt="pretty"))
        else:
            print(" No charge records found.")

    except Error as e:
        print(f" Database Error: {e}")

def category_wise_summary():
    try:

        cur.execute('''
        SELECT lc.item_name AS Payment_Category,
        COUNT(*) AS Total_Charges, SUM(CAST(c.paid_amt AS DECIMAL(10,2))) AS Total_Revenue
        FROM charges c LEFT JOIN lookup_code lc ON c.payment_category = lc.item_id
        GROUP BY lc.item_name
        ORDER BY Total_Revenue DESC
        ''')

        rows = cur.fetchall()
        header=[i[0] for i in cur.description]
        if rows:
            print(tabulate(rows, headers=header, tablefmt="pretty"))
        else:
            print("No charge records found.")

    except Error as e:
        print(f" Database Error: {e}")

def patient_wise_summary():
    try:
        cur.execute('''
        SELECT p.patient_name AS Patient, COUNT(*) AS Transactions,
        SUM(CAST(c.paid_amt AS DECIMAL(10,2))) AS Total_Spent
        FROM charges c
        LEFT JOIN tbl_consultation t ON c.cons_id = t.cons_id
        LEFT JOIN appointments a ON t.appt_id = a.appt_id
        LEFT JOIN patients p ON a.patient_id = p.patient_id
        GROUP BY p.patient_name
        ORDER BY Total_Spent DESC
        ''')

        rows = cur.fetchall()
        header=[i[0] for i in cur.description]
        if rows:
            print(tabulate(rows, headers=header, tablefmt="pretty"))
        else:
            print(" No patient transactions found.")

    except Error as e:
        print(f" Database Error: {e}")

def revenue_in_date_range():
    try:

        start_date = input("Enter start date (YYYY-MM-DD): ")
        end_date = input("Enter end date (YYYY-MM-DD): ")

        cur.execute('''
        SELECT DATE(c.payment_date) AS Date, COUNT(*) AS Transactions,
        SUM(CAST(c.paid_amt AS DECIMAL(10,2))) AS Revenue
        FROM charges c
        WHERE c.payment_date BETWEEN %s AND %s
        GROUP BY DATE(c.payment_date)
        ORDER BY Date ASC
        ''', (start_date, end_date))

        rows = cur.fetchall()
        header=[i[0] for i in cur.description]
        if rows:
            print(tabulate(rows, headers=header, tablefmt="pretty"))
        else:
            print(" No transactions found in that range.")

    except Error as e:
        print(f" Database Error: {e}")