import sys
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QSpinBox,QCheckBox, QMainWindow, QApplication, QDialog, QPushButton
from models import * 



db = SqliteDatabase('db/restaurnt.db')


with db:
    db.create_tables([Waiter, Table, Dish, Order, OrderItem, Receipt])

class LoginWindow(QMainWindow):

    def __init__(self):
        super(LoginWindow, self).__init__()

        uic.loadUi('ui/login.ui', self)
        self.login_pushButton.clicked.connect(self.login)
        self.register_pushButton.clicked.connect(self.open_register_window)
        self.show()

    def login(self):
        username = self.login_lineEdit.text()
        password = self.password_lineEdit.text()

        try:
            waiter = Waiter.get(Waiter.username == username)
            if waiter.check_password(password):
                self.main_window = MainWindow(waiter)
                self.main_window.show()
                self.close()
            else:
                QMessageBox.warning(self, "Ошибка", "Неверный пароль")
        except Waiter.DoesNotExist:
            QMessageBox.warning(self, "Ошибка", "Пользователь не найден")

    def open_register_window(self):
        self.register_window = RegisterWindow()
        self.register_window.show()

class RegisterWindow(QMainWindow):

    def __init__(self):
        super(RegisterWindow, self).__init__()
        uic.loadUi('ui/register.ui', self)
        self.save_pushButton.clicked.connect(self.register_user)
        self.goto_login_pushButton.clicked.connect(self.close)
        self.show()

    def register_user(self):
        username = self.login_lineEdit.text()
        password = self.password_lineEdit.text()

        try:
            Waiter.get(Waiter.username == username)
            QMessageBox.warning(self, "Ошибка", "Пользователь с таким именем уже существует")
        except Waiter.DoesNotExist:
            waiter = Waiter(username=username)
            waiter.set_password(password)
            waiter.save()
            QMessageBox.information(self, "Успех", "Пользователь зарегистрирован")
            self.close()

class OrderStatusWindow(QMainWindow):

    order_updated = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('ui/order_status_window.ui', self)
        self.load_orders()
        self.save_pushButton.clicked.connect(self.save_order_status)

    def load_orders(self):
        self.order_comboBox.clear()

        for order in Order.select():
            self.order_comboBox.addItem(f"Заказ #{order.id} (Стол: {order.table.table_number})", order.id)

    def save_order_status(self):
        order_id = self.order_comboBox.currentData()
        try:
            order = Order.get_by_id(order_id)
            order.is_completed = self.is_completed_checkBox.isChecked()
            order.is_paid = self.is_paid_checkBox.isChecked()
            order.save()
            QMessageBox.information(self, "Успех", "Статус заказа обновлен.")
            self.order_updated.emit()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка обновления статуса: {e}")

class OrderEditWindow(QMainWindow):

    order_updated = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('ui/order_edit_window.ui', self) 
        self.load_orders()
        self.delete_pushButton.clicked.connect(self.delete_order)

    def load_orders(self):
        self.order_comboBox.clear()

        for order in Order.select():
            self.order_comboBox.addItem(f"Заказ #{order.id} (Стол: {order.table.table_number})", order.id)

 
    def delete_order(self):
        order_id = self.order_comboBox.currentData()

        reply = QMessageBox.question(self, 'Удаление заказа',
                                     "Вы уверены, что хотите удалить заказ?",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                order = Order.get_by_id(order_id)
                order.delete_instance()
                self.order_updated.emit()
                self.load_orders()
                QMessageBox.information(self, "Успех", "Заказ успешно удален.")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления заказа: {e}")


class MainWindow(QMainWindow):

    def __init__(self, current_waiter):
        super(MainWindow, self).__init__()
        uic.loadUi('ui/main.ui', self)

        self.edit_order_button.clicked.connect(self.edit_order_window)
        self.add_order_pushButton.clicked.connect(self.open_add_order_window)
        self.open_order_status_button.clicked.connect(self.open_order_status_window)
        self.logout_pushButton.clicked.connect(self.logout)
        self.current_waiter = current_waiter
        self.tableWidget.setColumnCount(8)
        self.tableWidget.setHorizontalHeaderLabels(["ID", "Блюда", "Общая стоимость", "Выполнен", "Оплачен", "Официант", "Столик", "Дата"])
        self.load_orders()

    def open_order_status_window(self):
        self.order_status_window = OrderStatusWindow()
        self.order_status_window.show()
        self.order_status_window.order_updated.connect(self.load_orders)

    def load_orders(self):
        self.tableWidget.setRowCount(0)

        for order in Order.select():
            row_position = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row_position)
            order_items = OrderItem.select().where(OrderItem.order == order)
            dishes = ", ".join([f"{item.dish.name} ({item.quantity})" for item in order_items])
            total_cost = sum([item.dish.price * item.quantity for item in order_items])

            self.tableWidget.setItem(row_position, 0, QTableWidgetItem(str(order.id)))
            self.tableWidget.setItem(row_position, 1, QTableWidgetItem(dishes))
            self.tableWidget.setItem(row_position, 2, QTableWidgetItem(str(total_cost)))

            is_completed_checkbox = QCheckBox()
            is_completed_checkbox.setChecked(order.is_completed)
            is_completed_checkbox.setEnabled(False)
            self.tableWidget.setCellWidget(row_position, 3, is_completed_checkbox)

            is_paid_checkbox = QCheckBox()
            is_paid_checkbox.setChecked(order.is_paid)
            is_paid_checkbox.setEnabled(False)
            self.tableWidget.setCellWidget(row_position, 4, is_paid_checkbox)

            self.tableWidget.setItem(row_position, 5, QTableWidgetItem(order.waiter.username))
            self.tableWidget.setItem(row_position, 6, QTableWidgetItem(str(order.table.table_number)))
            self.tableWidget.setItem(row_position, 7, QTableWidgetItem(order.order_date.strftime("%Y-%m-%d %H:%M:%S")))

    def open_add_order_window(self):
        self.add_order_window = AddOrderWindow(self.current_waiter, self.load_orders)
        self.add_order_window.show()

    def logout(self):
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

    def edit_order_window(self):
        self.edit_order = OrderEditWindow()
        self.edit_order.show()
        self.edit_order.order_updated.connect(self.load_orders) 

class AddOrderWindow(QMainWindow):

    def __init__(self, current_waiter, refresh_orders_func):
        super().__init__()
        uic.loadUi('ui/add_order.ui', self)
        self.current_waiter = current_waiter
        self.refresh_orders_func = refresh_orders_func
        self.load_tables()
        self.load_dishes()
        self.save_order_pushButton.clicked.connect(self.save_order)

    def load_tables(self):
        self.table_comboBox.clear()
        for table in Table.select():
            self.table_comboBox.addItem(str(table.table_number), table.id)

    def load_dishes(self):
        self.dishes_tableWidget.setRowCount(0)
        self.dishes_tableWidget.setColumnCount(2)
        self.dishes_tableWidget.setHorizontalHeaderLabels(["Блюдо", "Количество"])

        row = 0
        for dish in Dish.select():
            self.dishes_tableWidget.insertRow(row)
            item = QTableWidgetItem(f"{dish.name} ({dish.price})")
            item.setData(QtCore.Qt.UserRole, dish.id)
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
            self.dishes_tableWidget.setItem(row, 0, item)

            spinbox = QSpinBox()
            spinbox.setMinimum(0)
            spinbox.setMaximum(100)
            self.dishes_tableWidget.setCellWidget(row, 1, spinbox)
            row += 1


    def save_order(self):

        try:
            selected_table_id = self.table_comboBox.currentData()

            dish_quantities = {}
            total_quantity = 0

            for row in range(self.dishes_tableWidget.rowCount()):
                item = self.dishes_tableWidget.item(row, 0)
                dish_id = item.data(QtCore.Qt.UserRole)
                spinbox = self.dishes_tableWidget.cellWidget(row, 1)
                quantity = spinbox.value()
                if quantity > 0:
                    dish_quantities[dish_id] = quantity
                    total_quantity += quantity

            if total_quantity == 0:
                QMessageBox.warning(self, "Внимание", "Заказ не может быть создан без добавления блюд в количестве больше нуля.")
                return

            new_order = Order.create(waiter=self.current_waiter, table=selected_table_id)
            order_created = True

            for dish_id, quantity in dish_quantities.items():
                dish = Dish.get_by_id(dish_id)
                OrderItem.create(order=new_order, dish=dish, quantity=quantity)

            QMessageBox.information(self, "Успех", "Заказ успешно создан.")
            self.close()
            self.refresh_orders_func()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при создании заказа: {e}")
            if new_order and order_created:
                new_order.delete_instance(recursive=True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    sys.exit(app.exec_())