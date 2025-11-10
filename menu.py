from mysql.connector import connect, Error
#user defined
from lookup_code import *
from user_creation import *
from inventories import *
from appointments import *
from tbl_consultation import *
from tbl_admission import *
from inpatient_procedures import *
from medication import *
from tests import *
from tbl_discharge import *
from charges import *

conn = connect(
        host = 'localhost',
        user = 'root',
        password = 'Fawaz@33448113',
        database = 'hospital'
)
cur = conn.cursor()

def staff_login():
    print('--Staff Login--')

    while True:
        user_name = input("Enter username : ")
        cur.execute('''SELECT staff_id, passcode, access_level from staff WHERE user_name = %s''', (user_name,))
        data = cur.fetchone()

        if not data:
            print("Username not found. Try again.")
            continue

        staff_id, passcode, access_level = data
        input_passcode = input("Enter passcode : ")
        if passcode == input_passcode:
            print(f"Login successful. Welcome {user_name}\n Redirecting...")
            return staff_id, access_level
        else:
            print("Incorrect password. Try again.")

def main_menu(staff_id, access_level):
    if access_level >= 9:
        while True:
            print("\n--Admin Menu--")
            print("1. Manage Staff")
            print("2. Manage Lookup Codes")
            print("3. Manage Inventory")
            print("4. Manage Medications")
            print("5. Manage Patients")
            print("6. Manage Appointments")
            print("7. Manage Consultations")
            print("8. Generate Reports")
            print("9. Logout")

            choice = input("Enter choice: ").strip()

            if choice == '1':
                while True:
                    print("\n--Staff Management--")
                    print("1. Create Staff")
                    print("2. Update Staff")
                    print("3. Back to Main Menu")
                    ch = input("Enter choice: ").strip()
                    if ch == '1':
                        create_staff(staff_id)
                    elif ch == '2':
                        update_staff(staff_id)
                    elif ch == '3':
                        break
                    else:
                        print("Invalid choice. Try again.")

            elif choice == '2':
                while True:
                    print("\n--Lookup Code Management--")
                    print("1. Add Item")
                    print("2. Update Item")
                    print("3. Remove Item")
                    print("4. Back to Main Menu")
                    ch = input("Enter choice: ").strip()
                    if ch == '1':
                        add_items_lookup_code(staff_id)
                    elif ch == '2':
                        update_items_lookup_code(staff_id)
                    elif ch == '3':
                        remove_items_lookup_code(staff_id)
                    elif ch == '4':
                        break
                    else:
                        print("Invalid choice. Try again.")

            elif choice == '3':
                while True:
                    print("\n--Inventory Management--")
                    print("1. View All Inventory")
                    print("2. Add Inventory")
                    print("3. Search Inventory")
                    print("4. Update Inventory")
                    print("5. Delete Inventory")
                    print("6. Back to Main Menu")
                    ch = input("Enter choice: ").strip()
                    if ch == '1':
                        view_all_inventories(staff_id)
                    elif ch == '2':
                        add_inventory(staff_id)
                    elif ch == '3':
                        search_inventory_by_name()
                    elif ch == '4':
                        update_inventory(staff_id)
                    elif ch == '5':
                        delete_inventory(staff_id)
                    elif ch == '6':
                        break
                    else:
                        print("Invalid choice. Try again.")

            elif choice == '4':
                while True:
                    print("\n--Medication Management--")
                    print("1. Add Medication")
                    print("2. View All Medications")
                    print("3. Update Medication")
                    print("4. Delete Medication")
                    print("5. Back to Main Menu")
                    ch = input("Enter choice: ").strip()
                    if ch == '1':
                        add_medication(staff_id)
                    elif ch == '2':
                        view_all_medications()
                    elif ch == '3':
                        update_medication(staff_id)
                    elif ch == '4':
                        delete_medication(staff_id)
                    elif ch == '5':
                        break
                    else:
                        print("Invalid choice. Try again.")

            elif choice == '5':
                while True:
                    print("\n--Patient Management--")
                    print("1. Create Patient")
                    print("2. Update Patient")
                    print("3. Back to Main Menu")
                    ch = input("Enter choice: ").strip()
                    if ch == '1':
                        create_patient(staff_id)
                    elif ch == '2':
                        update_patient(staff_id)
                    elif ch == '3':
                        break
                    else:
                        print("Invalid choice. Try again.")

            elif choice == '6':
                while True:
                    print("\n--Appointment Management--")
                    print("1. Book Appointment")
                    print("2. View Appointment")
                    print("3. Update Appointment")
                    print("4. Cancel Appointment")
                    print("5. List Doctor Schedule")
                    print("6. Back to Main Menu")
                    ch = input("Enter choice: ").strip()
                    '''if ch == '1':
                        book_appointment(staff_id)
                    elif ch == '2':
                        get_appointment()
                        get_patient_appointments()
                    elif ch == '3':
                        update_appointment_status(staff_id)
                    elif ch == '4':
                        cancel_appointment(staff_id)
                    elif ch == '5':
                        list_doctor_schedule()
                    elif ch == '6':
                        break
                    else:
                        print("Invalid choice. Try again.")

            elif choice == '7':
                while True:
                    print("\n--- Consultation Management ---")
                    print("1. Add Consultation")
                    print("2. Search Consultation")
                    print("3. Back to Main Menu")
                    ch = input("Enter choice: ").strip()
                    if ch == '1':
                        add_consultation(staff_id)
                    elif ch == '2':
                        search_consultation()
                    elif ch == '3':
                        break
                    else:
                        print("Invalid choice. Try again.")

            elif choice == '8':
                generate_reports()

            elif choice == '9':
                print("Logging out...")
                break

            else:
                print("Invalid choice. Try again.")

def main():
    staff_id, access_level = staff_login()
    main_menu(staff_id, access_level)'''