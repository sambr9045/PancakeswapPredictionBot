import mysql.connector
from mysql.connector import Error
import pandas as pd


class DB:
    def __init__(self, hostname, username, password, dbname=None):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.dbname = dbname

    def db_connector(self):
        connection = None
        try:
            connection= mysql.connector.connect(
                host=self.hostname,
                user=self.username,
                passwd=self.password,
                database=self.dbname

            )
            print("MySQL Database connection successful")
        except Error as err:
            print(f"Error: '{err}'")
        return connection

    # create database function
    def create_database(self, connection, query):
        cursor = connection.cursor()
        try:
            cursor.execute(query)
            print("Database created successfully")
        except Error as err:
            print(f"Error: '{err}'")

    def execute_query(self,db, query):
        cursor = db.cursor()
        try:
            cursor.execute(query)
            db.commit()
            print("Query successful")
        except Error as err:
            print(f"Error: '{err}'")

    def read_query(self, db, query):
        cursor = db.cursor()
        result = None
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Error as err:
            print(f"Error: '{err}'")


if __name__ == "__main__":
    # connection = DB("localhost", "root", "", "pancakeswapprediction")
    # db = connection.db_connector()
    # create_table = """
    #  CREATE TABLE BET(
    #  epoch  VARCHAR(100) NOT NULL,
    #  bear  FLOAT,
    #  bull  FLOAT,
    #  wallet_number INT NOT NULL,
    #  transaction_id VARCHAR(250),
    #  claimable BOOLEAN,
    #  datetime VARCHAR(250)
    #  )
    #  """
    # print(connection.execute_query(db, create_table))
    # # print(connection.read_query(db, "SELECT * FROM BET"))
    # print(connection.create_database(db, "CREATE DATABASE pancakeswapprediction"))
    pass