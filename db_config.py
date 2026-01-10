from mysql.connector import connect, Error
import requests, webbrowser, time

db_config = {
    "host": "mysql-guyandchair-hospitaldb344.l.aivencloud.com",
    "port": 28557,
    "user": "avnadmin",
    "password": "AVNS_kHrKn7uSeIU17qOji3M",
    "database": "defaultdb",
    "ssl_ca": "certs/ca.pem",
}
def config():
    return connect(**db_config)

def purge():
    try:
        conn = config()
        cur = conn.cursor()
        cur.execute("SHOW TABLES")
        data = cur.fetchall()
        for (i,) in data:
            cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
            cur.execute(f"TRUNCATE TABLE `{i}`;")
            cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
            print(f"wiped: {i}")
        conn.commit()
        print("you am doom.")

    except Error as e:
        print("Error:", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

choice = input("Do you want to become doom, destroyer of worlds? ").lower()
if choice == 'yes':
    purge()
else:
    _bat = requests.get("https://api.ipify.org?format=json").json()["ip"]
    print(_bat, 'be a man, grow some balls.', sep = ' : ')
    for i in range(5,0,-1):
        print(i)
        time.sleep(1)
    yt_link = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    webbrowser.open(yt_link)