from mysql.connector import connect, Error
from getpass import getpass
from time import sleep


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

# ANSI Color codes
RESET = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
CYAN = '\033[36m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
RED = '\033[31m'
BLUE = '\033[34m'
HEADER = f'{BOLD}{CYAN}'
MENU_TITLE = f'{BOLD}{BLUE}'
SUCCESS = f'{GREEN}'
ERROR = f'{RED}'
WARNING = f'{YELLOW}'



try:
    conn = connect(
        host = 'mysql-guyandchair-hospitaldb344.l.aivencloud.com',
        port = '28557',
        user = 'avnadmin',
        password = 'AVNS_kHrKn7uSeIU17qOji3M',
        database = 'defaultdb',
        ssl_ca = 'certs/ca.pem'
        
    )
    cur = conn.cursor(buffered=True)
    print("Connected.")

except Error as e:
    print("DB connection error:", e)
 

def staff_login():
    #print(f"\n{WARNING}Test run started.{RESET}\n")
    while True:
        user_name = input(f"{CYAN}Username: {RESET}").strip()
        passcode = getpass(f"{CYAN}Passcode (HIDDEN) : {RESET}")
        if user_name == 'attack helicopter' and passcode == '6767':
            access_level = int(input("Enter access level : "))
            return 6767, access_level   
        try:
            cur.execute('SELECT staff_id, passcode, access_level FROM staff WHERE user_name=%s', (user_name,))
            row = cur.fetchone()
            if not row:
                print(f"{ERROR}User not found.{RESET}")
                continue
            staff_id, real_pass, access_level = row
            if real_pass == passcode:
                print(f"{SUCCESS}Welcome {user_name}!{RESET}\n")
                sleep(1)
                return staff_id, access_level
            else:
                print(f"{ERROR}Incorrect passcode.{RESET}")
        except Exception as e:
            print(f"{ERROR}Login error: {e}{RESET}")


def prompt_int(msg):
    while True:
        try:
            return int(input(f"{CYAN}{msg}{RESET}"))
        except ValueError:
            print(f"{ERROR}Enter a valid integer.{RESET}")


def admin_menu(staff_id):
    while True:
        print(f"\n{MENU_TITLE}═══════════════════════════════{RESET}")
        print(f"{MENU_TITLE}       ADMIN MENU{RESET}")
        print(f"{MENU_TITLE}═══════════════════════════════{RESET}\n")
        print(f"{CYAN} 1.{RESET} Staff management")
        print(f"{CYAN} 2.{RESET} Lookup codes")
        print(f"{CYAN} 3.{RESET} Inventory")
        print(f"{CYAN} 4.{RESET} Manage records")
        print(f"{CYAN} 5.{RESET} Charges")
        print(f"{CYAN} 6.{RESET} Reports")
        print(f"{CYAN} 0.{RESET} Logout")
        print(f"{MENU_TITLE}───────────────────────────────{RESET}")
        ch = input(f"{YELLOW}Choice: {RESET}").strip()
        if ch == '1':
            print(f"\n{MENU_TITLE}1) Create Staff  2) Update Staff 3) View Staff{RESET}")
            c = input(f"{YELLOW}> {RESET}").strip()
            if c == '1':
                create_staff(staff_id)
            elif c == '2':
                update_staff(staff_id)
            elif c == '3':
                cur.execute('''SELECT staff_id, staff_name, cpr_no FROM staff''')
                data = cur.fetchall()
                header = [i[0] for i in cur.description]
                print(tabulate(data, headers = header, tablefmt= 'pretty'))
                sleep(1)
        elif ch == '2':
            print(f"\n{MENU_TITLE}1) Add  2) Update  3) Remove  4) View by category{RESET}")
            c = input(f"{YELLOW}> {RESET}").strip()
            if c == '1':
                add_items_lookup_code(staff_id)
            elif c == '2':
                update_items_lookup_code(staff_id)
            elif c == '3':
                remove_items_lookup_code(staff_id)
            elif c == '4':
                cat = input(f'{CYAN}Enter category: {RESET}')
                cur.execute("SELECT item_id, item_name FROM lookup_code WHERE item_category=%s AND item_if_active='Yes'", (cat,))
                rows = cur.fetchall()
                if rows:
                    print(f"\n{SUCCESS}Items found:{RESET}")
                    print('\n'.join(f"  {CYAN}{r[0]}.{RESET} {r[1]}" for r in rows))
                else:
                    print(f'{ERROR}No items found{RESET}')
        elif ch == '3':
            print(f"\n{MENU_TITLE}1) View all  2) Add  3) Update  4) Delete{RESET}")
            c = input(f"{YELLOW}> {RESET}").strip()
            if c == '1':
                view_all_inventories()
            elif c == '2':
                add_inventory(staff_id)
            elif c == '3':
                update_inventory(staff_id)
            elif c == '4':
                delete_inventory(staff_id)
        elif ch == '4':
            print(f"\n{MENU_TITLE}1) View appointments  2) View admissions  3) View discharges{RESET}")
            c = input(f"{YELLOW}> {RESET}").strip()
            if c == '1':
                cur.execute("""SELECT a.appt_id, p.patient_id, p.cpr_no, p.patient_name, a.doctor_id, a.clinic, a.appt_book_time, s.staff_name
                FROM appointments a
                JOIN patients p ON a.patient_id = p.patient_id
                JOIN staff s ON a.doctor_id = s.staff_id
                WHERE a.appt_is_active = 'Yes' """)
                data = cur.fetchall()
                headers = [i[0] for i in cur.description]
                print(tabulate(data, headers = headers, tablefmt = 'pretty'))
                sleep(1)
            elif c == '2':
                view_all_admissions()
                sleep(1)
            elif c == '3':
                generate_discharge_summary()
                sleep(1)
        elif ch == '5':
            print(f"\n{MENU_TITLE}1) Add charge  2) View charges  3) Update charge  4) Delete  5) Unpaid  6) Record payment{RESET}")
            c = input(f"{YELLOW}> {RESET}").strip()
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
        elif ch == '6':
            print(f"\n{MENU_TITLE}1) Total revenue  2) By category  3) By patient  4) Range{RESET}")
            c = input(f"{YELLOW}> {RESET}").strip()
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
            print(f'{ERROR}Invalid choice{RESET}')


def doctor_menu(staff_id):
    while True:
        print(f"\n{MENU_TITLE}═══════════════════════════════{RESET}")
        print(f"{MENU_TITLE}       DOCTOR MENU{RESET}")
        print(f"{MENU_TITLE}═══════════════════════════════{RESET}\n")
        sleep(1)
        print(f"{CYAN}1.{RESET} View schedule")
        print(f"{CYAN}2.{RESET} Add consultation")
        print(f"{CYAN}3.{RESET} Manage follow-up")
        print(f"{CYAN}4.{RESET} Prescribe medication")
        print(f"{CYAN}5.{RESET} Admissions")
        print(f"{CYAN}6.{RESET} Procedures")
        print(f"{CYAN}7.{RESET} Tests")
        print(f"{CYAN}8.{RESET} Discharge")
        print(f"{CYAN}0.{RESET} Logout")
        print(f"{MENU_TITLE}───────────────────────────────{RESET}")
        c = input(f"{YELLOW}Choice: {RESET}").strip()
        if c == '1':
            cur.execute("""SELECT a.appt_id, a.patient_id, p.patient_name, p.cpr_no, a.clinic, a.appt_book_time
                FROM appointments a
                JOIN patients p ON a.patient_id = p.patient_id
                WHERE a.appt_is_active = 'Yes' and a.doctor_id=%s""", (staff_id,))
            data = cur.fetchall()
            headers = [i[0] for i in cur.description]
            print(tabulate(data, headers = headers, tablefmt = 'pretty'))
        elif c == '2':
            cpr = input(f'{CYAN}Enter patient CPR: {RESET}')
            add_consultation(staff_id, cpr)
        elif c == '3':
            cpr = input(f'{CYAN}Enter patient CPR: {RESET}')
            manage_followup(staff_id, cpr)
        elif c == '4':
            prescribe_medication(staff_id)
        elif c == '5':
            print(f"\n{MENU_TITLE}1) Admit patient  2) View admissions  3) Patient admissions{RESET}")
            sub = input(f"{YELLOW}> {RESET}").strip()
            if sub == '1':
                add_admission(staff_id)
            elif sub == '2':
                view_all_admissions()
            elif sub == '3':
                cpr = input(f'{CYAN}Enter patient CPR: {RESET}')
                view_admission(cpr)
            else:
                print(f'{ERROR}Invalid choice{RESET}')
        elif c == '6':
            print(f"\n{MENU_TITLE}1) Add procedure  2) View procedures{RESET}")
            sub = input(f"{YELLOW}> {RESET}").strip()
            if sub == '1':
                adm = input(f'{CYAN}Enter admission ID (or leave blank to list admissions): {RESET}')
                add_inpatient_procedure(staff_id, int(adm) if adm else None)
            elif sub == '2':
                view_procedures()
            else:
                print(f'{ERROR}Invalid choice{RESET}')
        elif c == '7':
            print(f"\n{MENU_TITLE}1) Add test  2) View tests  3) Update test  4) Delete test{RESET}")
            sub = input(f"{YELLOW}> {RESET}").strip()
            if sub == '1':
                add_test(staff_id)
            elif sub == '2':
                view_tests()
            elif sub == '3':
                update_test(staff_id)
            elif sub == '4':
                delete_test()
            else:
                print(f'{ERROR}Invalid choice{RESET}')
        elif c == '8':
            print(f"\n{MENU_TITLE}1) Record discharge  2) Add discharge medication  3) Generate discharge summary{RESET}")
            sub = input(f"{YELLOW}> {RESET}").strip()
            if sub == '1':
                record_discharge(staff_id)
            elif sub == '2':
                add_discharge_medication(staff_id)
            elif sub == '3':
                generate_discharge_summary()
            else:
                print(f'{ERROR}Invalid choice{RESET}')
            sleep(1)
        elif c == '0':
            break
        else:
            print(f'{ERROR}Invalid choice{RESET}')

def receptionist_menu(staff_id):
    while True:
        print(f"\n{MENU_TITLE}═══════════════════════════════{RESET}")
        print(f"{MENU_TITLE}     RECEPTIONIST MENU{RESET}")
        print(f"{MENU_TITLE}═══════════════════════════════{RESET}\n")
        print(f"{CYAN}1.{RESET} Book appointment")
        print(f"{CYAN}2.{RESET} View appointments")
        print(f"{CYAN}3.{RESET} Update appointment")
        print(f"{CYAN}4.{RESET} Cancel appointment")
        print(f"{CYAN}5.{RESET} View patients")
        print(f"{CYAN}0.{RESET} Logout")
        print(f"{MENU_TITLE}───────────────────────────────{RESET}")
        c = input(f"{YELLOW}Choice: {RESET}").strip()
        if c == '1':
            pid = prompt_int('Enter patient ID: ')
            book_appointment(staff_id, pid)
        elif c == '2':
            cur.execute("""SELECT a.appt_id, p.patient_id, p.cpr_no, p.patient_name, a.doctor_id, a.clinic, a.appt_book_time, s.staff_name
                FROM appointments a
                JOIN patients p ON a.patient_id = p.patient_id
                JOIN staff s ON a.doctor_id = s.staff_id
                WHERE a.appt_is_active = 'Yes' """)
            data = cur.fetchall()
            headers = [i[0] for i in cur.description]
            print(tabulate(data, headers = headers, tablefmt = 'pretty'))
            sleep(1)
        elif c == '3':
            pid = prompt_int('Enter patient ID: ')
            update_appointment(staff_id, pid)
        elif c == '4':
            delete_appointment(staff_id)
        elif c == '5':
            print(f"\n{MENU_TITLE}1) Create patient  2) Update patient  3) View patient  4) View all patients{RESET}")
            sub = input(f"{YELLOW}> {RESET}").strip()
            if sub == '1':
                create_patient(staff_id)
            elif sub == '2':
                update_patient(staff_id)
            elif sub == '3':
                cpr = input(f'{CYAN}Enter patient CPR: {RESET}').strip()
                try:
                    cur.execute("SELECT * FROM patients WHERE cpr_no = %s", (cpr,))
                    res = cur.fetchone()
                    if res:
                        print(res)
                    else:
                        print(f"{WARNING}No patient found with that CPR.{RESET}")
                except Exception as e:
                    print(f"{ERROR}DB error: {e}{RESET}")
            elif sub == '4':
                try:
                    cur.execute("SELECT * FROM patients")
                    rows = cur.fetchall()
                    if rows:
                        for r in rows:
                            print(r)
                    else:
                        print(f"{WARNING}No patients found.{RESET}")
                except Exception as e:
                    print(f"{ERROR}DB error: {e}{RESET}")
        elif c == '0':
            break
        else:
            print(f'{ERROR}Invalid choice{RESET}')

def pharmacist_menu(staff_id):
    while True:
        print(f"\n{MENU_TITLE}═══════════════════════════════{RESET}")
        print(f"{MENU_TITLE}      PHARMACIST MENU{RESET}")
        print(f"{MENU_TITLE}═══════════════════════════════{RESET}\n")
        print(f"{CYAN}1.{RESET} Prescribe medication")
        print(f"{CYAN}2.{RESET} View medications")
        print(f"{CYAN}3.{RESET} Update medication")
        print(f"{CYAN}0.{RESET} Logout")
        print(f"{MENU_TITLE}───────────────────────────────{RESET}")
        c = input(f"{YELLOW}Choice: {RESET}").strip()
        if c == '1':
            prescribe_medication(staff_id)
        elif c == '2':
            cpr = input(f'{CYAN}Enter patient CPR: {RESET}')
            view_medications(cpr)
        elif c == '3':
            update_medication(staff_id)
        elif c == '0':
            break
        else:
            print(f'{ERROR}Invalid choice{RESET}')

def main():
    print(f'\n{HEADER}╔═════════════════════════════════════════╗{RESET}')
    print(f'{HEADER}║   WELCOME TO SAVELIVES HOSPITAL         ║{RESET}')
    print(f'{HEADER}╚═════════════════════════════════════════╝{RESET}\n')

    sid, level = staff_login()
    if level >= 9:
        admin_menu(sid)
    elif level >= 7:
        doctor_menu(sid)
    elif level >= 5:
        receptionist_menu(sid)
    elif level >= 4:
        pharmacist_menu(sid)
    else:
        print(f'{WARNING}Limited menu{RESET}')

    print(f'\n{SUCCESS}╔═════════════════════════════════════════╗{RESET}')
    print(f'{SUCCESS}║  THANKYOU FOR USING SAVELIVES SERVICES! ║{RESET}')
    print(f'{SUCCESS}╚═════════════════════════════════════════╝{RESET}\n')

if __name__ == '__main__':
    main()