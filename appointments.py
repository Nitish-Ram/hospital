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
    cur.execute('''CREATE TABLE IF NOT EXISTS appointments (
                appt_id INT AUTO_INCREMENT PRIMARY KEY,
                appt_his_id INT,
                patient_id INT,
                doctor_id INT,
                clinic INT,
                appt_book_time DATE,
                cons_fee_paid ENUM('Yes','No') DEFAULT 'No',
                cons_payment_receiptno INT,
                cons_paid_amount INT,
                appt_is_active ENUM('Yes','No') DEFAULT 'Yes',
                version INT DEFAULT 0,
                edited_by INT NULL,
                edited_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
                FOREIGN KEY (doctor_id) REFERENCES staff(staff_id),
                FOREIGN KEY (clinic) REFERENCES lookup_code(item_id)
                )''')
except Error as e:
    print(e)

def book_appointment(edited_by, patient_id):
    print("\n --- Book New Appointment ---")
    try:
        doctor_id = int(input("Enter Doctor ID: "))
        clinic = int(input("Enter Clinic ID (from lookup_code): "))
        appt_date = input("Enter Appointment Date (YYYY-MM-DD): ")
        query = """
        INSERT INTO appointments
        (appt_his_id, patient_id, doctor_id, clinic, appt_book_time)
        VALUES (%s, %s, %s, %s, %s)
        """
        cur.execute(query, (patient_id, doctor_id, clinic, appt_date))
        appt_id = cur.lastrowid
        appt_his_id = appt_id
        cur.execute ('''UPDATE appointments SET appt_his_id = %s
                     WHERE appt_id = %s''', (appt_his_id, appt_id))
        conn.commit
        print("Appointment booked successfully.")
    except ValueError:
        print(" Invalid input type. Please enter numbers where required.")
    except Error as e:
        print(f"  Error booking appointment: {e}")

def get_appointment():
    print("\n --- Get Appointment Details ---")
    try:
        appt_id = int(input("Enter Appointment ID: "))

        cur.execute("SELECT * FROM appointments WHERE appt_id = %s", (appt_id,))
        result = cur.fetchone()

        if result:
            print("\n Appointment Details:")
            header=[i for i in cur.description]
            print(tabulate(result,headers=header,tablefmt='pretty'))
            
        else:
            print(" Appointment not found.")

    except ValueError:
        print(" Invalid input type.")
    except Error as e:
        print(f" Error fetching appointment: {e}")

def get_patient_appointments():

    print("\n --- View Patient Appointments ---")
    try:
        patient_id = int(input("Enter Patient ID: "))

        cur.execute(
            "SELECT * FROM appointments WHERE patient_id = %s ORDER BY appt_book_time DESC",
            (patient_id,)
        )
        results = cur.fetchall()

        if results:
            header=[i for i in cur.description]
            print(f"\n Appointments for Patient ID {patient_id}:")
            print(tabulate(results,headers=header,tablefmt='pretty'))
            
        else:
            print(" No appointments found.")

    except ValueError:
        print(" Invalid Patient ID.")
    except Error as e:
        print(f" Error fetching appointments: {e}")

def update_appointment_status():
    print("\n --- Update Appointment Status ---")
    try:
        appt_id = int(input("Enter Appointment ID: "))
        status = input("Set status to 'Yes' (active) or 'No' (inactive): ").capitalize()

        if status not in ("Yes", "No"):
            print(" Invalid status. Use Yes/No only.")
            return

        cur.execute(
            "UPDATE appointments SET appt_is_active = %s, edited_on = NOW() WHERE appt_id = %s",
            (status, appt_id)
        )
        conn.commit()
        print(" Appointment status updated successfully.")
    except ValueError:
        print(" Invalid ID.")
    except Error as e:
        print(f" Error updating appointment: {e}")

def cancel_appointment():

    print("\n --- Cancel Appointment ---")
    try:
        appt_id = int(input("Enter Appointment ID to cancel: "))

        cur.execute(
            "UPDATE appointments SET appt_is_active = 'No', edited_on = NOW() WHERE appt_id = %s",
            (appt_id,)
        )
        conn.commit()
        print(f" Appointment {appt_id} cancelled successfully.")
    except ValueError:
        print(" Invalid Appointment ID.")
    except Error as e:
        print(f" Error cancelling appointment: {e}")

def list_doctor_schedule():

    print("\n --- Doctor Schedule ---")
    try:
        doctor_id = int(input("Enter Doctor ID: "))
        date_filter = input("Enter Date (YYYY-MM-DD) or leave blank for all: ")


        if date_filter.strip():
            cur.execute(
                "SELECT * FROM appointments WHERE doctor_id = %s AND appt_book_time = %s ORDER BY appt_book_time",
                (doctor_id, date_filter)
            )
        else:
            cur.execute(
                "SELECT * FROM appointments WHERE doctor_id = %s ORDER BY appt_book_time DESC",
                (doctor_id,)
            )

        results = cur.fetchall()
        if results:
            header=[i for i in cur.description]
            print(f"\n Schedule for Doctor ID {doctor_id}:")
            print(tabulate(results,headers=header,tablefmt='pretty'))
                
        else:
            print(" No appointments found.")
    except ValueError:
        print(" Invalid Doctor ID.")
    except Error as e:
        print(f" Error fetching doctor schedule: {e}")