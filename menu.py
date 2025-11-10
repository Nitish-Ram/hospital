from mysql.connector import connect, Error
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
    while True:
        print("\n--Main Menu--")

        #Admin
        if access_level >= 9:
            print("1. Manage Staff Accounts")
            print("2. Manage Lookup Codes")
            print("3. Manage Inventories")
            print("4. Manage Medications")
            print("5. Manage Patients")
            print("6. Manage Appointments")
            print("7. Manage Consultations")
            print("8. View Reports")
            print("9. Logout")

        #Doctor/Consultant
        elif access_level >= 7:
            print("1. Manage Patients")
            print("2. Manage Appointments")
            print("3. Manage Consultations")
            print("4. Manage Medication")
            print("5. Logout")

        #Nurse/Reception
        elif access_level >= 3:
            print("1. Manage Patients")
            print("2. Book Appointments")
            print("3. Record Procedures")
            print("4. Logout")

        else:
            print("Access level too low — contact admin.")
            break

        choice = input("\nEnter choice: ").strip()

        #for admin
        '''if access_level >= 9:
            if choice == '1':
                create_staff(staff_id)
                update_staff(staff_id)
            elif choice == '2':
                add_items_lookup_code(staff_id)
                update_items_lookup_code
                remove_items_lookup_code
            elif choice == '3':
                view_all_inventory(staff_id)
                add_inventory(staff_id)
                search_inventory_by_name()
                update_inventory(staff_id)
                delete_inventory(staff_id)
            elif choice == '4':
                add_medication(staff_id)
                view_all_medications()
                update_medication(staff_id)
                delete_medication(staff_id)
            elif choice == '5':
                create_patient(staff_id)
                update_patient(staff_id)
            elif choice == '6':
                manage_appointments(staff_id) #for now
            elif choice == '7':
                manage_consultations(staff_id) #for now
            elif choice == '8':
                generate_reports()
            elif choice == '9':
                print("Logging out...")
                break
            else:
                print("Invalid choice.")

        #for doctor
        elif access_level >= 7:
            if choice == '1':
                manage_patients(staff_id)
            elif choice == '2':
                manage_appointments(staff_id)
            elif choice == '3':
                manage_consultations(staff_id)
            elif choice == '4':
                update_medication(staff_id)
            elif choice == '5':
                print("Logging out...")
                break
            else:
                print("Invalid choice.")

        #for nurse or receptionist
        elif access_level >= 3:
            if choice == '1':
                manage_patients(staff_id)
            elif choice == '2':
                manage_appointments(staff_id)
            elif choice == '3':
                record_procedure(staff_id)
            elif choice == '4':
                print("Logging out...")
                break
            else:
                print("Invalid choice.")'''

def main():
    staff_id, access_level = staff_login()
    main_menu(staff_id, access_level)