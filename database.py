import mysql.connector
from mysql.connector import Error

class Database:
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = "Ramoncito12."
        self.database = "renta_mobiliario_nacional"
        self.connection = None
        self.connect()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print("Connected to MySQL database")
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            self.connection = None

    def execute_query(self, query, params=None, fetch=False):
        if not self.connection or not self.connection.is_connected():
            print("No database connection. Attempting to reconnect...")
            self.connect()
            if not self.connection or not self.connection.is_connected():
                print("Failed to reconnect to database.")
                return False

        cursor = self.connection.cursor(dictionary=True)
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            if fetch:
                result = cursor.fetchall()
                return result
            self.connection.commit()
            return True
        except Error as e:
            print(f"Database error: {e}")
            return False
        finally:
            cursor.close()

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")