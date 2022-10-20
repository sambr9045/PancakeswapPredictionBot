import db as database
import  pprint
# fetch deta
db_connection = database.DB("localhost", "root", "", "pancakeswapprediction")
connection = db_connection.db_connector()
query = """ SELECT * FROM BET"""
# query2 = """DROP TABLE BET"""
data = db_connection.read_query(connection, query)
for i in data:
    print(pprint.pprint(i))

