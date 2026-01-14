import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

RDS_HOST = os.getenv("RDS_HOST")
RDS_USER = os.getenv("RDS_USER")
RDS_PASSWORD = os.getenv("RDS_PASSWORD")
RDS_DB = os.getenv("RDS_DB")

def connect_db():
    return pymysql.connect(
        host=RDS_HOST,
        user=RDS_USER,
        password=RDS_PASSWORD,
        database=RDS_DB,
        cursorclass=pymysql.cursors.DictCursor
    )

def check_user_exists(user_id):
    try:
        connection = connect_db()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE customerId = %s", (user_id,))
            result = cursor.fetchone()
        connection.close()
        return result  # Will be None if user doesn't exist
    except Exception as e:
        print(f"DB error: {e}")
        return None


def insert_user_into_rds(user_data):
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO users 
                (customerId, firstName, lastName, age, city, email, accountBalance, creditLimit, creditCardBalance)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                user_data["customerId"],
                user_data["firstName"],
                user_data["lastName"],
                int(user_data["age"]),
                user_data["city"],
                user_data["email"],
                int(user_data["accountBalance"]),
                int(user_data["creditLimit"]),
                int(user_data["creditCardBalance"])
            ))
            connection.commit()
    finally:
        connection.close()