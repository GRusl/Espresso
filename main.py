import sys

import sqlite3

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDialog


class EmployeeDlg(QDialog):
    def __init__(self, parent=None, num=None):
        super().__init__(parent)
        uic.loadUi('addEditCoffeeForm.ui', self)

        self.parent = parent
        self.num = num

        self.update_combo_box()

        if num:
            result = get_write_data(num)[0]
            print(result)
            self.lineEdit.setText(str(result[0]))
            if self.comboBox.findText(str(result[1])) != -1:
                self.comboBox.setCurrentIndex(self.comboBox.findText(str(result[1])))
            self.spinBox.setValue(result[2])
            self.checkBox.setChecked(result[3] == "true")
            self.textEdit.setPlainText(result[4])
            self.doubleSpinBox.setValue(result[5])
            self.spinBox_2.setValue(result[6])

        '''
        result = cur.execute("""SELECT title FROM Varieties""").fetchall()
        '''

        # self.comboBox.addItems(list(map(lambda x: x[0], result)))

        self.pushButton.clicked.connect(self.add_update_date)
        self.pushButton_2.clicked.connect(self.delete_variety)
        self.pushButton_3.clicked.connect(self.add_variety)

    def update_combo_box(self):
        result = list(map(lambda x: str(x[0]), cur.execute("""SELECT title FROM Varieties""").fetchall()))

        print(result)

        try:
            if self.comboBox.count():
                self.comboBox.clear()
            if self.comboBox_2.count():
                self.comboBox_2.clear()

            self.comboBox.addItems(result)
            self.comboBox_2.addItems(result)
        except Exception as e:
            print(e)

    def add_variety(self):
        try:
            cur.execute(f"""INSERT INTO Varieties (title) VALUES ('{self.lineEdit_2.text()}')""").fetchall()
            con.commit()

            self.update_combo_box()
        except Exception as e:
            print(e)

    def delete_variety(self):
        try:
            cur.execute(f"""DELETE FROM Varieties WHERE title = '{self.comboBox_2.currentText()}'""").fetchall()
            con.commit()

            self.update_combo_box()
        except Exception as e:
            print(e)

    def add_update_date(self):
        try:
            if self.num:
                cur.execute(f"""UPDATE Coffee
                                SET
                                    title = '{self.lineEdit.text()}',
                                    variety = (SELECT ID FROM Varieties WHERE title = '{self.comboBox.currentText()}'),
                                    degree_roasting = {self.spinBox.value()},
                                    ground = '{"true" if self.checkBox.isChecked() else "false"}',
                                    description = '{self.textEdit.toPlainText()}',
                                    price = {self.doubleSpinBox.value()},
                                    volume = {self.spinBox_2.value()}
                                WHERE ID = {self.num}""").fetchall()
            else:
                print(self.checkBox.isChecked(), '---------')
                cur.execute(f"""INSERT INTO Coffee (
                                    title,
                                    variety,
                                    degree_roasting,
                                    ground,
                                    description,
                                    price,
                                    volume
                                ) VALUES (
                                    '{self.lineEdit.text()}',
                                    (SELECT ID FROM Varieties WHERE title = '{self.comboBox.currentText()}'),
                                    {self.spinBox.value()},
                                    '{"true" if self.checkBox.isChecked() else "false"}',
                                    '{self.textEdit.toPlainText()}',
                                    {self.doubleSpinBox.value()},
                                    {self.spinBox_2.value()}
                                )""").fetchall()

            con.commit()

            self.parent.update_table()
        except Exception as e:
            print(e)


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)

        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels(('Название', 'Сорт', 'Степень обжарки',
                                                    'Формат', 'Описание вкуса', 'Цена', 'Объем упаковки'))

        self.pushButton.clicked.connect(self.update_table)
        self.pushButton_2.clicked.connect(lambda: EmployeeDlg(self).exec())
        self.pushButton_3.clicked.connect(self.update_data)

        self.update_table()

    def update_data(self):
        result = cur.execute(f"""SELECT ID FROM Coffee WHERE title = '{self.lineEdit.text()}'""").fetchall()
        if result:
            EmployeeDlg(self, result[0][0]).exec()

    def update_table(self):
        result = get_write_data()

        self.tableWidget.setRowCount(len(result))
        for i, row in enumerate(result):
            for k, item in enumerate(row):
                if k == 3:
                    item = "Молотый" if item == 'true' else 'В зернах'
                self.tableWidget.setItem(i, k, QTableWidgetItem(str(item)))

        self.tableWidget.resizeColumnsToContents()


def get_write_data(data_id=None):
    return cur.execute(f"""SELECT Coffee.title, Varieties.title, Coffee.degree_roasting, Coffee.ground, Coffee.description, Coffee.price, Coffee.volume
                           FROM
                               Coffee
                           LEFT OUTER JOIN
                               Varieties
                           ON Coffee.variety = Varieties.ID
                           {f"WHERE Coffee.ID = {data_id}" if data_id else ""}""").fetchall()


if __name__ == '__main__':
    con = sqlite3.connect("coffee.sqlite")
    cur = con.cursor()

    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
