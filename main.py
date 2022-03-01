import sys

import sqlite3

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)

        self.con = sqlite3.connect("coffee.sqlite")
        self.cur = self.con.cursor()

        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels(('Название', 'Сорт', 'Степень обжарки',
                                                    'Формат', 'Описание вкуса', 'Цена', 'Объем упаковки'))

        self.pushButton.clicked.connect(self.run)

        self.run()

    def run(self):
        result = self.cur.execute("""SELECT Coffee.title, Varieties.title, Coffee.degree_roasting, Coffee.ground, Coffee.description, Coffee.price, Coffee.volume
                                     FROM
                                         Coffee
                                     LEFT OUTER JOIN
                                         Varieties
                                     ON Coffee.variety = Varieties.ID""").fetchall()

        self.tableWidget.setRowCount(len(result))
        for i, row in enumerate(result):
            for k, item in enumerate(row):
                if k == 3:
                    item = "Молотый" if item == 'true' else 'В зернах'
                self.tableWidget.setItem(i, k, QTableWidgetItem(str(item)))

        self.tableWidget.resizeColumnsToContents()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
