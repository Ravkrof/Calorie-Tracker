import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QMainWindow, QApplication, QCompleter, QComboBox, QMessageBox, QDialog
import datetime
from cal_main import Ui_MainWindow
from database import MySqlDB
import decimal


class MainWindow:
    def __init__(self):
        # Initializing main app window
        self.main_win = QMainWindow()
        self.main_win.setFixedSize(1101, 761)

        # Adding ui file
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.main_win)

        # Initializing Mysql Cursor
        self.sql = MySqlDB()  # calories database
        self.cursor = self.sql.dbcursor

        # Initializing Global Variables
        self.user=""
        self.uid=""

        # Initializing functions
        self.home()
        self.add()
        self.history()
        self.login()
        self.signup()

        # Setting Main Page
        self.ui.stackedWidget.setCurrentWidget(self.ui.page)

    def login(self):
        self.ui.pushButton_2.clicked.connect(self.goto_signup)
        self.ui.pushButton.clicked.connect(self.login_button)

    def loginsql(self, email):
        try:
            self.cursor.execute("Select password from users where email = %s", (email,))
            tmp = self.cursor.fetchone()[0]
            print("function")
            return tmp

        except Exception as e:
            print(e)
            showErrorMessage("Your haven't registered with us", "Error", "Invalid Credentials")
            return None


    def login_button(self):
        email = self.ui.lineEdit.text()
        password = self.ui.lineEdit_2.text()
        auth = False
        print(email, password)
        passwordDB = self.loginsql(email)
        print(passwordDB)
        if passwordDB != None:
            if password == passwordDB:
                auth = True
            else:
                auth = False
        if auth == True:
            self.cursor.execute("Select u_name from users where email = %s", (email,))
            self.user = self.cursor.fetchone()[0]
            self.cursor.execute("Select u_id from users where email = %s", (email,))
            self.uid = self.cursor.fetchone()[0]
            print(self.user)
            self.ui.label_12.setText(self.user)
            self.goto_home()
        else:
            showErrorMessage("Your email or password is incorrect", "Error", "Invalid Credentials")

    def signup(self):
        self.ui.pushButton_7.clicked.connect(self.signup_submit)
        self.ui.pushButton_11.clicked.connect(self.signup_return)

    def signup_submit(self):
        name = self.ui.lineEdit_3.text()
        password = self.ui.lineEdit_4.text()
        age = self.ui.lineEdit_5.text()
        weight = self.ui.lineEdit_6.text()
        height = self.ui.lineEdit_7.text()
        email = self.ui.lineEdit_8.text()
        print(name, password, age, weight, height, email)
        self.cursor.execute("insert into users(u_name,age,weight,height,password,email) values(%s,%s,%s,%s,%s,%s)",(name,age,weight,height,password,email))
        self.goto_login()

    def signup_return(self):
        self.goto_login()

    def home(self):
        self.ui.pushButton_3.clicked.connect(self.goto_history)
        self.ui.pushButton_4.clicked.connect(self.goto_add)
        self.ui.pushButton_5.clicked.connect(self.goto_login)

    def add(self):
        self.ui.pushButton_6.clicked.connect(self.add_button)
        self.ui.pushButton_10.clicked.connect(self.add_return_button)

    def add_button(self):
        dishname = self.ui.comboBox.currentText()
        print(dishname)
        datetime1 = self.ui.dateTimeEdit_3.dateTime()
        qty = self.ui.lineEdit_9.text()
        tot_cal=1
        try:
            self.cursor.execute("select d_id from dishes where d_name = %s",(dishname,))
            d_id = int(self.cursor.fetchone()[0])
            print(d_id)
            self.cursor.execute("select u_id from users where u_name = %s", (self.user,))
            u_id = int(self.cursor.fetchone()[0])
            self.cursor.execute("select d_calories from dishes where d_id =%s",(d_id,))
            tot_cal = int(self.cursor.fetchone()[0])
            tot_cal = decimal.Decimal(tot_cal)*decimal.Decimal(qty)
            datetime1 = datetime1.toPyDateTime()
            #datetime1 =  datetime1.strftime('%Y-%m-%d %H:%M:%S')
            t = f"{datetime1.year}-{datetime1.month}-{datetime1.day} {datetime1.hour}:{datetime1.minute}:{datetime1.second}"
            self.cursor.execute("insert into eats(u_id,d_id,quantity,tot_calories,date_time) values(%s,%s,%s,%s,%s)",(u_id,d_id,qty,tot_cal,t))
        except Exception as e:
            print (e)
        self.goto_home()

    def add_return_button(self):
        self.goto_home()

    def history(self):
        self.ui.pushButton_9.clicked.connect(self.history_return_button)
        self.ui.pushButton_8.clicked.connect(self.history_compute_button)

    def history_return_button(self):
        self.goto_home()

    def getStoredProcedureData(self):
        for result in self.cursor.stored_results():
            return result.fetchall()

    def history_compute_button(self):
        datetime1 = self.ui.dateTimeEdit.dateTime()
        datetime2 = self.ui.dateTimeEdit_2.dateTime()
        self.cursor.callproc('view_history', (self.uid,datetime1.toString("yyyy-MM-dd HH:mm:ss"),datetime2.toString("yyyy-MM-dd HH:mm:ss") ))
        l1 = self.getStoredProcedureData()
        self.cursor.callproc('totcal_for_date_range', (self.uid, datetime1.toString("yyyy-MM-dd HH:mm:ss"), datetime2.toString("yyyy-MM-dd HH:mm:ss")))
        l2 = self.getStoredProcedureData()
        self.ui.label_18.setText(str(l2[0][1]) +" Calories")

        # Adding columns to table
        self.ui.tableWidget.setRowCount(len(l1))
        self.ui.tableWidget.setColumnCount(4)
        self.ui.tableWidget.setHorizontalHeaderLabels(["Dish Name","Quantity","Calories","Datetime"])

        header = self.ui.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        # adding data into tables
        row = 0

        for record in l1:
            self.ui.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(str(record[0])))
            self.ui.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(str(record[1])))
            self.ui.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem(str(record[2])))
            self.ui.tableWidget.setItem(row, 3, QtWidgets.QTableWidgetItem(str(record[3])))
            row += 1

    def goto_home(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_3)
        datetime1=datetime.datetime.now().replace(hour=00,minute=00,second=00,microsecond=00)
        datetime2=datetime.datetime.now().replace(microsecond=00)
        self.cursor.callproc('totcal_for_date_range', (self.uid, datetime1, datetime2))
        l2 = self.getStoredProcedureData()
        if l2[0][1] is not None:
            self.ui.label_13.setText(str(l2[0][1])+" Calories")
        else:
            self.ui.label_13.setText(str("0 Calories"))

    def goto_add(self):
        l = ["cheese omelet", "garlic cheese toast", "tomato soup", "pav bhaji", "palak paneer", "butter naan", "poha", "rava idli ", "strawberry milkshake", "ghee rice", "peanut chutney", "french fries", "onion pakoda", "poori", "masoor dal", "paneer butter masala", "aloo paratha", "samosa"]
        self.ui.comboBox.blockSignals(True)
        self.ui.comboBox.clear()
        self.ui.comboBox.addItems(l)  # pass list inside
        self.ui.comboBox.blockSignals(False)
        self.ui.dateTimeEdit_3.setDateTime(datetime.datetime.now())
        self.ui.lineEdit_3.setText("")
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_5)

    def goto_history(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_4)

    def goto_login(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page)

    def goto_signup(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_2)


def showErrorMessage(message, win_title, title):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle(win_title)
    msg.setText(title)
    msg.setInformativeText(message)
    msg.exec_()



if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        main_win = MainWindow()
        main_win.main_win.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(e)

