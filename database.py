import mysql.connector
class MySqlDB:

    def connectToDatabase(self):
        try:

            self.db = mysql.connector.connect(
                host="localhost",
                user="root",
                passwd="Jay@suresh123",
                database="caloriecounter"
            )
            self.dbcursor = self.db.cursor()
            self.db.autocommit = True

            print("Connected to Database Successfully")

            return self.dbcursor

        except Exception as e:
            print("Error connecting to database")
            print(e)
            quit(-1)


    def __init__(self):
        try:
            self.dbcursor = self.connectToDatabase()
        except Exception as e:
            print(e)


