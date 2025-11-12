from mysql.connector import connect, Error
from getpass import getpass


# import application modules
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
from summary import *



try:
    conn = connect(
        host = 'mysql-guyandchair-hospitaldb344.l.aivencloud.com',
        port = '28557',
        user = 'avnadmin',
        password = 'AVNS_kHrKn7uSeIU17qOji3M',
        database = 'defaultdb',
        ssl_ca = 'certs/ca.pem'
    )
    print("Connected.")
    cur = conn.cursor()
except Error as e:
    print("DB connection error:", e)
 

def staff_login():
    print("Test run started.")
    while True:
        user_name = input("Username: ").strip()
        passcode = getpass("Passcode: ")
        try:
            cur.execute('SELECT staff_id, passcode, access_level FROM staff WHERE user_name=%s', (user_name,))
            row = cur.fetchone()
            if not row:
                print("User not found.")
                continue
            staff_id, real_pass, access_level = row
            if real_pass == passcode:
                print(f"Welcome {user_name}!")
                return staff_id, access_level
            else:
                print("Incorrect passcode.")
        except Exception as e:
            print("Login error:", e)


def prompt_int(msg):
    while True:
        try:
            return int(input(msg))
        except ValueError:
            print("Enter a valid integer.")


def admin_menu(staff_id):
    while True:
        print('\n-- Admin Menu --')
        print('1. Staff management')
        print('2. Lookup codes')
        print('3. Inventory')
        print('4. Medication')
        print('5. Patients')
        print('6. Appointments')
        print('7. Consultations')
        print('8. Admissions')
        print('9. Procedures')
        print('10. Tests')
        print('11. Discharge')
        print('12. Charges')
        print('13. Reports')
        print('0. Logout')
        ch = input('Choice: ').strip()
        if ch == '1':
            print('\n1) Create Staff  2) Update Staff')
            c = input('> ').strip()
            if c == '1':
                create_staff(staff_id)
            elif c == '2':
                update_staff(staff_id)
        elif ch == '2':
            print('\n1) Add 2) Update 3) Remove 4) View by category')
            c = input('> ').strip()
            if c == '1':
                add_items_lookup_code(staff_id)
            elif c == '2':
                update_items_lookup_code(staff_id)
            elif c == '3':
                remove_items_lookup_code(staff_id)
            elif c == '4':
                cat = input('Enter category: ')
                cur.execute('SELECT item_id, item_name FROM lookup_code WHERE item_category=%s AND item_if_active="Yes"', (cat,))
                rows = cur.fetchall()
                if rows:
                    print('\n'.join(f"{r[0]}. {r[1]}" for r in rows))
                else:
                    print('No items found')
        elif ch == '3':
            print('\n1) View all 2) Add 3) Search 4) Update 5) Delete')
            c = input('> ').strip()
            if c == '1':
                view_all_inventories()
            elif c == '2':
                add_inventory(staff_id)
            elif c == '3':
                search_inventory_by_name()
            elif c == '4':
                update_inventory(staff_id)
            elif c == '5':
                delete_inventory(staff_id)
        elif ch == '4':
            print('\n1) Prescribe 2) View all 3) Update 4) Delete')
            c = input('> ').strip()
            if c == '1':
                prescribe_medication(staff_id)
            elif c == '2':
                view_all_medications()
            elif c == '3':
                update_medication(staff_id)
            elif c == '4':
                delete_medication()
        elif ch == '5':
            print('\n1) Create patient 2) Update patient 3) View admissions for patient')
            c = input('> ').strip()
            if c == '1':
                create_patient(staff_id)
            elif c == '2':
                update_patient(staff_id)
            elif c == '3':
                pid = prompt_int('Enter patient ID: ')
                get_patient_admissions(pid)
        elif ch == '6':
            print('\n1) Book 2) View all 3) Update 4) Cancel')
            c = input('> ').strip()
            if c == '1':
                pid = prompt_int('Enter patient ID: ')
                book_appointment(staff_id, pid)
            elif c == '2':
                view_appointment()
            elif c == '3':
                pid = prompt_int('Enter patient ID: ')
                update_appointment(staff_id, pid)
            elif c == '4':
                delete_appointment(staff_id)
        elif ch == '7':
            print('\n1) Add consultation 2) Manage follow-up 3) View consultations')
            c = input('> ').strip()
            if c == '1':
                cpr = input('Enter patient CPR: ')
                add_consultation(staff_id, cpr)
            elif c == '2':
                cpr = input('Enter patient CPR: ')
                manage_followup(staff_id, cpr)
            elif c == '3':
                print('Use SQL or custom viewer in tbl_consultation module.')
        elif ch == '8':
            print('\n1) Admit patient 2) View admissions 3) Update admission 4) Patient admissions')
            c = input('> ').strip()
            if c == '1':
                add_admission(staff_id)
            elif c == '2':
                view_admissions()
            elif c == '3':
                update_admission(staff_id)
            elif c == '4':
                pid = prompt_int('Enter patient ID: ')
                get_patient_admissions(pid)
        elif ch == '9':
            print('\n1) Add procedure 2) View procedures')
            c = input('> ').strip()
            if c == '1':
                adm = input('Enter admission ID (or leave blank to list admissions): ')
                add_inpatient_procedure(staff_id, int(adm) if adm else None)
            elif c == '2':
                view_procedures()
        elif ch == '10':
            print('\n1) Add test 2) View tests 3) Update test 4) Delete test')
            c = input('> ').strip()
            if c == '1':
                add_test(staff_id)
            elif c == '2':
                view_tests()
            elif c == '3':
                update_test(staff_id)
            elif c == '4':
                delete_test()
        elif ch == '11':
            print('\n1) Record discharge 2) Add discharge medication 3) Generate discharge summary')
            c = input('> ').strip()
            if c == '1':
                record_discharge(staff_id)
            elif c == '2':
                add_discharge_medication(staff_id)
            elif c == '3':
                generate_discharge_summary()
        elif ch == '12':
            print('\n1) Add charge 2) View charges 3) Update charge 4) Delete 5) Unpaid 6) Record payment')
            c = input('> ').strip()
            if c == '1':
                add_charge(staff_id)
            elif c == '2':
                view_charges()
            elif c == '3':
                update_charge_status(staff_id)
            elif c == '4':
                delete_charge()
            elif c == '5':
                get_unpaid_charges()
            elif c == '6':
                record_payment(staff_id)
        elif ch == '13':
            print('\n1) Total revenue 2) By category 3) By patient 4) Range')
            c = input('> ').strip()
            if c == '1':
                total_revenue_summary()
            elif c == '2':
                category_wise_summary()
            elif c == '3':
                patient_wise_summary()
            elif c == '4':
                revenue_in_date_range()
        elif ch == '0':
            break
        else:
            print('Invalid choice')


def doctor_menu(staff_id):
    while True:
        print('\n-- Doctor Menu --')
        print('1. View schedule')
        print('2. Add consultation')
        print('3. Manage follow-up')
        print('4. Prescribe medication')
        print('0. Logout')
        c = input('> ').strip()
        if c == '1':
            print('Use appointments.view_appointment or implement list_doctor_schedule in appointments module')
        elif c == '2':
            cpr = input('Enter patient CPR: ')
            add_consultation(staff_id, cpr)
        elif c == '3':
            cpr = input('Enter patient CPR: ')
            manage_followup(staff_id, cpr)
        elif c == '4':
            prescribe_medication(staff_id)
        elif c == '0':
            break
        else:
            print('Invalid')


def main():
    sid, level = staff_login()
    if level >= 9:
        admin_menu(sid)
    elif level >= 7:
        doctor_menu(sid)
    else:
        print('Limited menu: view appointments and personal info')

if __name__ == '__main__':
    main()