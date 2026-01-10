from mysql.connector import connect, Error
from getpass import getpass
from time import sleep
from tabulate import tabulate

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
from db_config import config

# ANSI Color codes
RESET = '\033[0m'
BOLD = '\033[1m'
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
    conn = config()
    cur = conn.cursor(buffered=True)
    print("Connected.")
except Error as e:
    print("DB connection error:", e)

def staff_login():
    while True:
        user_name = input(f"{CYAN}Username: {RESET}").strip()
        passcode = getpass(f"{CYAN}Passcode : (HIDDEN){RESET}")
        if user_name == 'attack helicopter' and passcode == '6767':
            access_level = int(input("Enter access level: "))
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

# -------------------- Patient Care Workflow --------------------
def patient_care_workflow(staff_id):
    while True:
        cpr_no = input(f'{CYAN}Enter patient CPR (or "back" to exit): {RESET}').strip()
        if cpr_no.lower() == 'back':
            break

        cur.execute("SELECT * FROM patients WHERE cpr_no=%s", (cpr_no,))
        patient = cur.fetchone()
        if not patient:
            choice = input(f"{WARNING}Patient not found. Create new patient? (y/n): {RESET}").strip().lower()
            if choice == 'y':
                create_patient(staff_id)
            continue

        while True:
            print(f"\n{MENU_TITLE}--- Patient Care Options ---{RESET}")
            print(f"{CYAN}1.{RESET} Add consultation")
            print(f"{CYAN}2.{RESET} Admit patient")
            print(f"{CYAN}3.{RESET} Discharge patient")
            print(f"{CYAN}0.{RESET} Back to Doctor Menu")
            action = input(f"{YELLOW}Choice: {RESET}").strip()

            if action == '1':
                discharged, test, cons_id = add_consultation(staff_id, cpr_no)
                conn.commit()
                if not cons_id:
                    print(f"{WARNING}No consultation created for this patient.{RESET}")
                    continue

                followup_exists = False
                try:
                    cur.execute("SELECT * FROM followup WHERE cons_id=%s", (cons_id,))
                    if cur.fetchone():
                        followup_exists = True
                except Error:
                    followup_exists = False

                while True:
                    print(f"\n{MENU_TITLE}--- Consultation Options ---{RESET}")
                    option_num = 1
                    if followup_exists:
                        print(f"{CYAN}{option_num}.{RESET} Manage follow-up")
                        option_num += 1
                    print(f"{CYAN}{option_num}.{RESET} Add tests")
                    option_num += 1
                    print(f"{CYAN}{option_num}.{RESET} Admit patient")
                    option_num += 1
                    print(f"{CYAN}{option_num}.{RESET} Discharge patient")
                    print(f"{CYAN}0.{RESET} Back")
                    choice = input(f"{YELLOW}Choice: {RESET}").strip()

                    if followup_exists:
                        if choice == '1':
                            manage_followup(cons_id)
                            conn.commit()
                        elif choice == '2':
                            add_test_cons(staff_id, cons_id)
                            conn.commit()
                        elif choice == '3':
                            add_admission(staff_id, cpr_no)
                            conn.commit()
                            break
                        elif choice == '4':
                            record_discharge(staff_id, cpr_no)
                            conn.commit()
                            break
                        elif choice == '0':
                            break
                        else:
                            print(f"{ERROR}Invalid choice{RESET}")
                    else:
                        if choice == '1':
                            add_test_cons(staff_id, cons_id)
                            conn.commit()
                        elif choice == '2':
                            add_admission(staff_id, cpr_no)
                            conn.commit()
                            break
                        elif choice == '3':
                            record_discharge(staff_id, cpr_no)
                            conn.commit()
                            break
                        elif choice == '0':
                            break
                        else:
                            print(f"{ERROR}Invalid choice{RESET}")

                if discharged == 'yes':
                    record_discharge(staff_id, cpr_no)
                    conn.commit()
                break

            elif action == '2':
                adm_id = add_admission(staff_id, cpr_no)
                conn.commit()
                if not adm_id:
                    print(f"{WARNING}Admission failed or already exists.{RESET}")
                    continue
                while True:
                    print(f"\n{MENU_TITLE}--- Inpatient Options ---{RESET}")
                    print(f"{CYAN}1.{RESET} Add inpatient procedure")
                    print(f"{CYAN}2.{RESET} Add tests")
                    print(f"{CYAN}3.{RESET} Prescribe medication")
                    print(f"{CYAN}4.{RESET} View admission details")
                    print(f"{CYAN}5.{RESET} Discharge patient")
                    print(f"{CYAN}0.{RESET} Back to Patient Menu")
                    sub = input(f"{YELLOW}Choice: {RESET}").strip()

                    if sub == '1':
                        add_inpatient_procedure(staff_id, cpr_no)
                        conn.commit()
                    elif sub == '2':
                        add_test_adm(staff_id, adm_id)
                        conn.commit()
                    elif sub == '3':
                        prescribe_medication_adm(adm_id,staff_id)
                        conn.commit()
                    elif sub == '4':
                        view_procedures(cpr_no)
                        conn.commit()
                    elif sub == '5':
                        record_discharge(staff_id, cpr_no)
                        conn.commit()
                        break
                    elif sub == '0':
                        break
                    else:
                        print(f'{ERROR}Invalid choice{RESET}')
                break

            elif action == '3':
                record_discharge(staff_id, cpr_no)
                conn.commit()
                break

            elif action == '0':
                break

            else:
                print(f'{ERROR}Invalid choice{RESET}')

# -------------------- Doctor Menu --------------------
def doctor_menu(staff_id):
    while True:
        print(f"\n{MENU_TITLE}═══════════════════════════════{RESET}")
        print(f"{MENU_TITLE}       DOCTOR MENU{RESET}")
        print(f"{MENU_TITLE}═══════════════════════════════{RESET}\n")
        sleep(1)
        print(f"{CYAN}1.{RESET} View schedule")
        print(f"{CYAN}2.{RESET} Patient Care Workflow")
        print(f"{CYAN}3.{RESET} View all admissions")
        print(f"{CYAN}4.{RESET} Admission procedures")
        print(f"{CYAN}5.{RESET} View tests")
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
            print(tabulate(data, headers=headers, tablefmt='pretty'))
            input("\nPress any key to exit to menu.")
        elif c == '2':
            patient_care_workflow(staff_id)
        elif c == '3':
            view_all_admissions()
            sleep(1)
        elif c == '4':
            adm_id = prompt_int('Enter Admission ID: ')
            print(f"\n{MENU_TITLE}1) Tests  2) View procedures{RESET}")
            sub = input(f"{YELLOW}> {RESET}").strip()
            if sub == '1':
                ch = input(f"{CYAN}1.add tests 2.update tests 3.delete tests: {RESET}").strip().lower()
                if ch == '1':
                    cur.execute(''' SELECT item_id,item_name from lookup_code 
                        where item_category = 'Imaging' or item_category='Lab' ''')
                    data=cur.fetchall()
                    print(tabulate(data,headers=['id','name'],tablefmt='pretty'))
                    add_test_adm(staff_id, adm_id)
                    conn.commit()
                elif ch == '2':
                    update_test(staff_id)
                    conn.commit()
                elif ch == '3':
                    delete_test()
                    conn.commit()
                else:
                    print(f'{ERROR}Invalid choice{RESET}')
            elif sub == '2':
                print(f"{CYAN}1.{RESET} Add inpatient procedure")
                print(f"{CYAN}2.{RESET} Add tests")
                print(f"{CYAN}3.{RESET} Prescribe medication")
                print(f"{CYAN}4.{RESET} View admission details")
                print(f"{CYAN}5.{RESET} Discharge patient")
                print(f"{CYAN}6.{RESET} View inpatient procedures")
                print(f"{CYAN}0.{RESET} Back to Patient Menu")
                ch = input(f"{YELLOW}Choice: {RESET}").strip()
                cpr_no=prompt_int('enter cpr no: ')
                if sub == '1':
                    add_inpatient_procedure(staff_id, cpr_no)
                    conn.commit()
                elif sub == '2':
                    add_test_adm(staff_id, adm_id)
                    conn.commit()
                elif sub == '3':
                    prescribe_medication_adm(adm_id,staff_id)
                    conn.commit()
                elif sub == '4':
                    view_procedures(cpr_no)
                    conn.commit()
                elif sub == '5':
                    record_discharge(staff_id, cpr_no)
                    conn.commit()
                    break
                elif ch=='6':
                    view_procedures(cpr_no)
                elif sub == '0':
                    break
                else:
                    print(f'{ERROR}Invalid choice{RESET}')
            else:
                print(f'{ERROR}Invalid choice{RESET}')
        elif c == '5':
            view_tests()
        elif c == '0':
            conn.commit()
            break
        else:
            print(f'{ERROR}Invalid choice{RESET}')

# -------------------- Receptionist Menu --------------------
def receptionist_menu(staff_id):
    while True:
        print(f"\n{MENU_TITLE}═══════════════════════════════{RESET}")
        print(f"{MENU_TITLE}     RECEPTIONIST MENU{RESET}")
        print(f"{MENU_TITLE}═══════════════════════════════{RESET}\n")
        print(f"{CYAN}1.{RESET} Book appointment")
        print(f"{CYAN}2.{RESET} View appointments")
        print(f"{CYAN}3.{RESET} Update appointment")
        print(f"{CYAN}4.{RESET} Cancel appointment")
        print(f"{CYAN}5.{RESET} Patients")
        print(f"{CYAN}0.{RESET} Logout")
        print(f"{MENU_TITLE}───────────────────────────────{RESET}")
        c = input(f"{YELLOW}Choice: {RESET}").strip()
        if c == '1':
            pid = prompt_int('Enter patient cpr: ')
            book_appointment(staff_id, pid)
        elif c == '2':
            sub=input(f"\n{MENU_TITLE}1) View by CPR  2) View all appointments{RESET}\n{YELLOW}> {RESET}").strip()
            if sub=='1':    
                cpr = input(f'{CYAN}Enter patient CPR: {RESET}').strip()
                view_appointment(cpr)
            elif sub=='2':
                view_all_appointment()
            else:
                print(f'{ERROR}Invalid choice{RESET}')
            sleep(1)
        elif c == '3':
            pid = prompt_int('Enter patient cpr: ')
            update_appointment(staff_id, pid)
        elif c == '4':
            pid = prompt_int('Enter patient cpr: ')
            delete_appointment(staff_id,pid)
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
                        headers = [i[0] for i in cur.description]
                        print(tabulate([res], headers=headers, tablefmt='pretty'))
                    else:
                        print(f"{WARNING}No patient found with that CPR.{RESET}")
                except Exception as e:
                    print(f"{ERROR}DB error: {e}{RESET}")
            elif sub == '4':
                try:
                    cur.execute("SELECT * FROM patients")
                    rows = cur.fetchall()
                    if rows:
                        headers = [i[0] for i in cur.description]
                        print(tabulate(rows, headers=headers, tablefmt='pretty'))
                    else:
                        print(f"{WARNING}No patients found.{RESET}")
                except Exception as e:
                    print(f"{ERROR}DB error: {e}{RESET}")
        elif c == '0':
            conn.commit()
            break
        else:
            print(f'{ERROR}Invalid choice{RESET}')

# -------------------- Pharmacist Menu --------------------
def pharmacist_menu(staff_id):
    while True:
        print(f"\n{MENU_TITLE}═══════════════════════════════{RESET}")
        print(f"{MENU_TITLE}      PHARMACIST MENU{RESET}")
        print(f"{MENU_TITLE}═══════════════════════════════{RESET}\n")
        print(f"{CYAN}1.{RESET} Prescribe medication(admission)")
        print(f"{CYAN}2.{RESET} View medications")
        print(f"{CYAN}0.{RESET} Logout")
        print(f"{MENU_TITLE}───────────────────────────────{RESET}")
        c = input(f"{YELLOW}Choice: {RESET}").strip()
        if c == '1':
            cpr = input(f'{CYAN}Enter patient CPR: {RESET}')
            c=view_admission(cpr)
            if c:
                adm_id=input(f'{CYAN}Enter Admission ID: {RESET}')
                prescribe_medication_adm(adm_id,staff_id)
        elif c == '2':
            cpr = input(f'{CYAN}Enter patient CPR: {RESET}')
            view_medications(cpr)
        elif c == '0':
            conn.commit()
            break
        else:
            print(f'{ERROR}Invalid choice{RESET}')

# -------------------- Admin Menu --------------------
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
            print(f"\n{MENU_TITLE}1) Create Staff  2) Update Staff  3) View Staff{RESET}")
            c = input(f"{YELLOW}> {RESET}").strip()
            if c == '1':
                create_staff(staff_id)
                conn.commit()
            elif c == '2':
                update_staff(staff_id)
                conn.commit()
            elif c == '3':
                cur.execute('SELECT staff_id, staff_name, cpr_no FROM staff')
                data = cur.fetchall()
                headers = [i[0] for i in cur.description]
                print(tabulate(data, headers=headers, tablefmt='pretty'))
                sleep(1)
        elif ch == '2':
            print(f"\n{MENU_TITLE}1) Add  2) Update  3) Remove  4) View by category{RESET}")
            c = input(f"{YELLOW}> {RESET}").strip()
            if c == '1':
                add_items_lookup_code(staff_id)
                conn.commit()
            elif c == '2':
                update_items_lookup_code(staff_id)
                conn.commit()
            elif c == '3':
                remove_items_lookup_code(staff_id)
                conn.commit()
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
                conn.commit()
            elif c == '2':
                add_inventory(staff_id)
                conn.commit()
            elif c == '3':
                update_inventory(staff_id)
                conn.commit()
            elif c == '4':
                delete_inventory(staff_id)
                conn.commit()
        elif ch == '4':
            print(f"\n{MENU_TITLE}1) View appointments  2) View admissions  3) View discharges{RESET}")
            c = input(f"{YELLOW}> {RESET}").strip()
            if c == '1':
                view_all_appointment()
                sleep(1)
            elif c == '2':
                view_all_admissions()
                sleep(1)
            elif c == '3':
                generate_discharge_summary()
                sleep(1)
        elif ch == '5':
            print(f"\n{MENU_TITLE}1) Add charge  2) View charges  3) Update charge  4) Unpaid  5) Record payment{RESET}")
            c = input(f"{YELLOW}> {RESET}").strip()
            if c == '1':
                add_charge(staff_id)
                conn.commit()
            elif c == '2':
                view_charges()
            elif c == '3':
                update_charge_status(staff_id)
                conn.commit()
            elif c == '4':
                get_unpaid_charges()
            elif c == '5':
                record_payment(staff_id)
                conn.commit()
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
            conn.commit()
            break
        else:
            print(f'{ERROR}Invalid choice{RESET}')

# -------------------- Main --------------------
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