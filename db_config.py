from mysql.connector import connect

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