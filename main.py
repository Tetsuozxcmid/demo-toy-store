import os
import random
import string
import sys
import uuid
from decimal import Decimal
from PIL import Image
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor, QFont, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
import db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "images")
PLACEHOLDER_IMAGE = os.path.join(IMAGES_DIR, "picture.png")
LOGO_IMAGE = os.path.join(IMAGES_DIR, "icon.png")
ICON_PATH = os.path.join(IMAGES_DIR, "icon.ico")
COLOR_BACKGROUND = "#FFFFFF"
COLOR_ACCENT = "#00FA9A"
COLOR_BUTTON = "#7FFF00"
COLOR_HEADER = "#2E8B57"
COLOR_DISCOUNT_HIGH = "#FFDEAD"
COLOR_OUT_OF_STOCK = "#ADD8E6"
COLOR_PRICE_OLD = "#FF0000"
COLOR_PRICE_NEW = "#000000"
MAIN_FONT = QFont("Times New Roman", 11)
HEADER_FONT = QFont("Times New Roman", 14, QFont.Weight.Bold)
PRODUCT_EDIT_WINDOW = None


def ensure_directories():
    os.makedirs(IMAGES_DIR, exist_ok=True)


def resolve_image_path(image_path):
    if not image_path:
        return PLACEHOLDER_IMAGE
    if os.path.isabs(image_path) and os.path.exists(image_path):
        return image_path
    candidate = os.path.join(BASE_DIR, image_path.replace("/", os.sep))
    if os.path.exists(candidate):
        return candidate
    folder = os.path.dirname(candidate)
    name = os.path.basename(candidate)
    if os.path.isdir(folder):
        for file_name in os.listdir(folder):
            if file_name.lower() == name.lower():
                return os.path.join(folder, file_name)
    return PLACEHOLDER_IMAGE


def generate_product_article():
    alphabet = string.ascii_uppercase + string.digits
    while True:
        article = "".join(random.choices(alphabet, k=6))
        if not db.article_exists(article):
            return article


def apply_main_style(widget):
    widget.setFont(MAIN_FONT)
    widget.setStyleSheet(
        f"\n        QWidget {{\n            background-color: {COLOR_BACKGROUND};\n            color: #000000;\n        }}\n        QPushButton {{\n            background-color: {COLOR_BUTTON};\n            border: 1px solid #555555;\n            border-radius: 4px;\n            padding: 6px 12px;\n            min-height: 28px;\n        }}\n        QPushButton:hover {{\n            background-color: {COLOR_ACCENT};\n        }}\n        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QTextEdit {{\n            border: 1px solid #AAAAAA;\n            padding: 4px;\n            background-color: #FFFFFF;\n        }}\n        QTableWidget {{\n            gridline-color: #CCCCCC;\n            selection-background-color: {COLOR_ACCENT};\n        }}\n        QHeaderView::section {{\n            background-color: {COLOR_HEADER};\n            color: #FFFFFF;\n            padding: 6px;\n            border: 1px solid #FFFFFF;\n            font-weight: bold;\n        }}\n        "
    )


def load_pixmap(image_path, width=80, height=60):
    path = resolve_image_path(image_path)
    pixmap = QPixmap(path)
    if pixmap.isNull():
        pixmap = QPixmap(PLACEHOLDER_IMAGE)
    return pixmap.scaled(
        width,
        height,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )


def calculate_final_price(price, discount_percent):
    price_value = Decimal(str(price))
    discount_value = Decimal(str(discount_percent))
    final_price = price_value * (Decimal("100") - discount_value) / Decimal("100")
    return final_price.quantize(Decimal("0.01"))


def format_price_text(price, discount_percent):
    final_price = calculate_final_price(price, discount_percent)
    if discount_percent and float(discount_percent) > 0:
        return f'<span style="color:{COLOR_PRICE_OLD}; text-decoration: line-through;">{price:.2f} ₽</span> <span style="color:{COLOR_PRICE_NEW};">{final_price:.2f} ₽</span>'
    return f"{price:.2f} ₽"


def save_product_image(source_path):
    image = Image.open(source_path)
    image.thumbnail((300, 200), Image.Resampling.LANCZOS)
    file_name = f"product_{uuid.uuid4().hex}.png"
    destination = os.path.join(IMAGES_DIR, file_name)
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    image.save(destination, format="PNG")
    return os.path.join("images", file_name)


def remove_image_file(image_path):
    if not image_path:
        return
    full_path = resolve_image_path(image_path)
    images_abs = os.path.abspath(IMAGES_DIR)
    file_abs = os.path.abspath(full_path)
    if file_abs.startswith(images_abs) and os.path.basename(full_path) != "picture.png":
        try:
            os.remove(file_abs)
        except OSError:
            pass


class HeaderWidget(QWidget):

    def __init__(self, title_text, user_name="", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        logo_label = QLabel()
        logo_label.setPixmap(load_pixmap(LOGO_IMAGE, 120, 48))
        layout.addWidget(logo_label)
        title_label = QLabel(title_text)
        title_label.setFont(HEADER_FONT)
        title_label.setStyleSheet(f"color: {COLOR_HEADER};")
        layout.addWidget(title_label)
        layout.addStretch()
        user_label = QLabel(user_name if user_name else "Гость")
        user_label.setFont(HEADER_FONT)
        user_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        layout.addWidget(user_label)


class LoginWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход в систему — Магазин игрушек")
        self.setMinimumSize(480, 320)
        self.current_user = None
        self._build_ui()
        apply_main_style(self)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.addWidget(HeaderWidget("Авторизация"))
        form_group = QGroupBox("Введите логин и пароль")
        form_layout = QFormLayout(form_group)
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Логин")
        form_layout.addRow("Логин:", self.login_input)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Пароль:", self.password_input)
        layout.addWidget(form_group)
        buttons_layout = QHBoxLayout()
        login_button = QPushButton("Войти")
        login_button.clicked.connect(self.handle_login)
        buttons_layout.addWidget(login_button)
        guest_button = QPushButton("Войти как гость")
        guest_button.clicked.connect(self.handle_guest)
        buttons_layout.addWidget(guest_button)
        layout.addLayout(buttons_layout)
        layout.addStretch()

    def handle_login(self):
        login_value = self.login_input.text().strip()
        password_value = self.password_input.text().strip()
        if not login_value or not password_value:
            QMessageBox.warning(
                self, "Предупреждение", "Заполните логин и пароль для входа в систему."
            )
            return
        try:
            user_data = db.authenticate_user(login_value, password_value)
        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось выполнить авторизацию.\n\n{error}\n\nПроверьте подключение к базе данных и повторите попытку.",
            )
            return
        if not user_data:
            QMessageBox.warning(
                self,
                "Ошибка авторизации",
                "Неверный логин или пароль.\nПроверьте введённые данные и попробуйте снова.",
            )
            return
        self.open_products_window(user_data)

    def handle_guest(self):
        guest_data = {
            "user_id": 0,
            "login": "guest",
            "full_name": "Гость",
            "role_name": "guest",
        }
        self.open_products_window(guest_data)

    def open_products_window(self, user_data):
        self.products_window = ProductsWindow(user_data, self)
        self.products_window.show()
        self.hide()

    def show_login_again(self):
        self.login_input.clear()
        self.password_input.clear()
        self.show()


class ProductsWindow(QMainWindow):

    def __init__(self, user_data, login_window):
        super().__init__()
        self.user_data = user_data
        self.login_window = login_window
        self.role_name = user_data["role_name"]
        self.can_filter = self.role_name in ("manager", "admin")
        self.can_edit = self.role_name == "admin"
        self.can_view_orders = self.role_name in ("manager", "admin")
        self.setWindowTitle("Список товаров — Магазин игрушек")
        self.setMinimumSize(1200, 700)
        self._build_ui()
        apply_main_style(self)
        self.load_products()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.addWidget(
            HeaderWidget("Список товаров", self.user_data.get("full_name", ""))
        )
        if self.can_filter:
            filter_layout = QHBoxLayout()
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("Поиск по текстовым полям...")
            self.search_input.textChanged.connect(self.load_products)
            filter_layout.addWidget(QLabel("Поиск:"))
            filter_layout.addWidget(self.search_input)
            self.supplier_filter = QComboBox()
            self.supplier_filter.addItem("Все поставщики", None)
            try:
                suppliers = db.fetch_suppliers()
                for supplier in suppliers:
                    self.supplier_filter.addItem(
                        supplier["supplier_name"], supplier["supplier_id"]
                    )
            except Exception as error:
                QMessageBox.critical(
                    self, "Ошибка", f"Не удалось загрузить поставщиков.\n\n{error}"
                )
            self.supplier_filter.currentIndexChanged.connect(self.load_products)
            filter_layout.addWidget(QLabel("Поставщик:"))
            filter_layout.addWidget(self.supplier_filter)
            self.sort_field = QComboBox()
            self.sort_field.addItem("Без сортировки", "")
            self.sort_field.addItem("Количество на складе", "quantity")
            self.sort_field.addItem("Цена", "price")
            self.sort_field.currentIndexChanged.connect(self.load_products)
            filter_layout.addWidget(QLabel("Сортировка:"))
            filter_layout.addWidget(self.sort_field)
            self.sort_order = QComboBox()
            self.sort_order.addItem("По возрастанию", "ASC")
            self.sort_order.addItem("По убыванию", "DESC")
            self.sort_order.currentIndexChanged.connect(self.load_products)
            filter_layout.addWidget(self.sort_order)
            layout.addLayout(filter_layout)
        self.table = QTableWidget()
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels(
            [
                "Фото",
                "Наименование",
                "Категория",
                "Описание",
                "Производитель",
                "Поставщик",
                "Цена",
                "Ед. изм.",
                "Кол-во",
                "Скидка, %",
                "ID",
            ]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Fixed
        )
        self.table.setColumnWidth(0, 90)
        self.table.setColumnHidden(10, True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        if self.can_edit:
            self.table.cellDoubleClicked.connect(self.open_edit_product)
        layout.addWidget(self.table)
        buttons_layout = QHBoxLayout()
        if self.can_edit:
            add_button = QPushButton("Добавить товар")
            add_button.clicked.connect(self.open_add_product)
            buttons_layout.addWidget(add_button)
            delete_button = QPushButton("Удалить товар")
            delete_button.clicked.connect(self.delete_selected_product)
            buttons_layout.addWidget(delete_button)
        if self.can_view_orders:
            orders_button = QPushButton("Заказы")
            orders_button.clicked.connect(self.open_orders)
            buttons_layout.addWidget(orders_button)
        back_button = QPushButton("Назад")
        back_button.clicked.connect(self.go_back)
        buttons_layout.addWidget(back_button)
        logout_button = QPushButton("Выход")
        logout_button.clicked.connect(self.logout)
        buttons_layout.addWidget(logout_button)
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

    def get_filter_params(self):
        if not self.can_filter:
            return ("", None, "", "ASC")
        search_text = self.search_input.text().strip()
        supplier_id = self.supplier_filter.currentData()
        sort_field = self.sort_field.currentData()
        sort_order = self.sort_order.currentData()
        return (search_text, supplier_id, sort_field, sort_order)

    def load_products(self):
        search_text, supplier_id, sort_field, sort_order = self.get_filter_params()
        try:
            products = db.fetch_products(
                search_text, supplier_id, sort_field, sort_order
            )
        except Exception as error:
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось загрузить список товаров.\n\n{error}"
            )
            return
        self.table.setRowCount(len(products))
        for row_index, product in enumerate(products):
            self.table.setRowHeight(row_index, 70)
            photo_label = QLabel()
            photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            photo_label.setPixmap(load_pixmap(product.get("image_path")))
            self.table.setCellWidget(row_index, 0, photo_label)
            values = [
                product["product_name"],
                product["category_name"],
                product["description"] or "",
                product["manufacturer_name"],
                product["supplier_name"],
                "",
                product["unit_name"],
                str(product["quantity"]),
                f"{product['discount_percent']:.0f}%",
                str(product["product_id"]),
            ]
            for column_index, value in enumerate(values, start=1):
                if column_index == 6:
                    price_label = QLabel(
                        format_price_text(product["price"], product["discount_percent"])
                    )
                    price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setCellWidget(row_index, 6, price_label)
                    continue
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row_index, column_index, item)
            self.apply_row_style(row_index, product)

    def apply_row_style(self, row_index, product):
        quantity = int(product["quantity"])
        discount = float(product["discount_percent"])
        if quantity == 0:
            background_color = COLOR_OUT_OF_STOCK
        elif discount > 17:
            background_color = COLOR_DISCOUNT_HIGH
        else:
            background_color = COLOR_BACKGROUND
        for column_index in range(self.table.columnCount()):
            if column_index == 0:
                widget = self.table.cellWidget(row_index, column_index)
                if widget:
                    widget.setStyleSheet(f"background-color: {background_color};")
                continue
            if column_index == 6:
                widget = self.table.cellWidget(row_index, column_index)
                if widget:
                    widget.setStyleSheet(f"background-color: {background_color};")
                continue
            item = self.table.item(row_index, column_index)
            if item:
                item.setBackground(QColor(background_color))

    def open_add_product(self):
        global PRODUCT_EDIT_WINDOW
        if PRODUCT_EDIT_WINDOW is not None:
            QMessageBox.warning(
                self,
                "Предупреждение",
                "Уже открыто окно редактирования товара.\nЗакройте его перед открытием нового.",
            )
            PRODUCT_EDIT_WINDOW.raise_()
            PRODUCT_EDIT_WINDOW.activateWindow()
            return
        dialog = ProductEditDialog(None, self)
        PRODUCT_EDIT_WINDOW = dialog
        dialog.exec()
        PRODUCT_EDIT_WINDOW = None
        self.load_products()

    def open_edit_product(self, row, column):
        global PRODUCT_EDIT_WINDOW
        if PRODUCT_EDIT_WINDOW is not None:
            QMessageBox.warning(
                self,
                "Предупреждение",
                "Уже открыто окно редактирования товара.\nЗакройте его перед открытием другого.",
            )
            PRODUCT_EDIT_WINDOW.raise_()
            PRODUCT_EDIT_WINDOW.activateWindow()
            return
        product_id_item = self.table.item(row, 10)
        if not product_id_item:
            return
        product_id = int(product_id_item.text())
        dialog = ProductEditDialog(product_id, self)
        PRODUCT_EDIT_WINDOW = dialog
        dialog.exec()
        PRODUCT_EDIT_WINDOW = None
        self.load_products()

    def delete_selected_product(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(
                self, "Предупреждение", "Выберите товар в таблице для удаления."
            )
            return
        row = selected_rows[0].row()
        product_id_item = self.table.item(row, 10)
        product_name_item = self.table.item(row, 1)
        if not product_id_item or not product_name_item:
            QMessageBox.warning(
                self, "Предупреждение", "Не удалось определить выбранный товар."
            )
            return
        product_id = int(product_id_item.text())
        product_name = product_name_item.text()
        try:
            product = db.fetch_product_by_id(product_id)
        except Exception as error:
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось определить товар.\n\n{error}"
            )
            return
        if db.is_product_in_orders(product_id):
            QMessageBox.warning(
                self,
                "Запрещено",
                f"Товар «{product_name}» присутствует в заказе и не может быть удалён.",
            )
            return
        answer = QMessageBox.question(
            self,
            "Подтверждение",
            f"Вы действительно хотите удалить товар «{product_name}»?\nЭто действие необратимо.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            remove_image_file(product.get("image_path"))
            db.delete_product(product_id)
            QMessageBox.information(self, "Информация", "Товар успешно удалён.")
            self.load_products()
        except Exception as error:
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось удалить товар.\n\n{error}"
            )

    def open_orders(self):
        self.orders_window = OrdersWindow(self.user_data, self)
        self.orders_window.show()
        self.hide()

    def go_back(self):
        self.close()
        self.login_window.show_login_again()

    def logout(self):
        self.go_back()


class ProductEditDialog(QDialog):

    def __init__(self, product_id, parent_window):
        super().__init__(parent_window)
        self.product_id = product_id
        self.parent_window = parent_window
        self.current_image_path = None
        self.is_edit_mode = product_id is not None
        title = "Редактирование товара" if self.is_edit_mode else "Добавление товара"
        self.setWindowTitle(f"{title} — Магазин игрушек")
        self.setMinimumSize(520, 620)
        self._build_ui()
        apply_main_style(self)
        if self.is_edit_mode:
            self.load_product_data()
        else:
            self.id_label.setText(str(db.get_next_product_id()))
            self.photo_label.setPixmap(load_pixmap(None, 300, 200))

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(
            HeaderWidget(
                "Редактирование товара" if self.is_edit_mode else "Добавление товара",
                self.parent_window.user_data.get("full_name", ""),
            )
        )
        form_layout = QFormLayout()
        self.id_label = QLineEdit()
        self.id_label.setReadOnly(True)
        self.article_label = QLineEdit()
        self.article_label.setReadOnly(True)
        if self.is_edit_mode:
            form_layout.addRow("ID товара:", self.id_label)
            form_layout.addRow("Артикул:", self.article_label)
        else:
            self.id_label.setVisible(False)
            self.article_label.setVisible(False)
        self.photo_label = QLabel()
        self.photo_label.setFixedSize(300, 200)
        self.photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photo_label.setFrameShape(QFrame.Shape.Box)
        form_layout.addRow("Фото:", self.photo_label)
        photo_button = QPushButton("Загрузить фото")
        photo_button.clicked.connect(self.load_photo)
        form_layout.addRow("", photo_button)
        self.name_input = QLineEdit()
        form_layout.addRow("Наименование:", self.name_input)
        self.category_combo = QComboBox()
        for category in db.fetch_categories():
            self.category_combo.addItem(
                category["category_name"], category["category_id"]
            )
        form_layout.addRow("Категория:", self.category_combo)
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        form_layout.addRow("Описание:", self.description_input)
        self.manufacturer_combo = QComboBox()
        for manufacturer in db.fetch_manufacturers():
            self.manufacturer_combo.addItem(
                manufacturer["manufacturer_name"], manufacturer["manufacturer_id"]
            )
        form_layout.addRow("Производитель:", self.manufacturer_combo)
        self.supplier_combo = QComboBox()
        for supplier in db.fetch_suppliers():
            self.supplier_combo.addItem(
                supplier["supplier_name"], supplier["supplier_id"]
            )
        form_layout.addRow("Поставщик:", self.supplier_combo)
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 9999999.99)
        self.price_input.setDecimals(2)
        self.price_input.setSuffix(" ₽")
        form_layout.addRow("Цена:", self.price_input)
        self.unit_input = QLineEdit()
        self.unit_input.setText("шт.")
        form_layout.addRow("Ед. измерения:", self.unit_input)
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(0, 999999)
        form_layout.addRow("Кол-во на складе:", self.quantity_input)
        self.discount_input = QDoubleSpinBox()
        self.discount_input.setRange(0, 100)
        self.discount_input.setDecimals(2)
        self.discount_input.setSuffix(" %")
        form_layout.addRow("Скидка:", self.discount_input)
        layout.addLayout(form_layout)
        buttons_layout = QHBoxLayout()
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_product)
        buttons_layout.addWidget(save_button)
        back_button = QPushButton("Назад")
        back_button.clicked.connect(self.reject)
        buttons_layout.addWidget(back_button)
        layout.addLayout(buttons_layout)

    def load_product_data(self):
        try:
            product = db.fetch_product_by_id(self.product_id)
        except Exception as error:
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось загрузить данные товара.\n\n{error}"
            )
            self.reject()
            return
        if not product:
            QMessageBox.warning(self, "Ошибка", "Товар не найден в базе данных.")
            self.reject()
            return
        self.id_label.setText(str(product["product_id"]))
        self.article_label.setText(product["article"])
        self.current_image_path = product.get("image_path")
        self.photo_label.setPixmap(load_pixmap(self.current_image_path, 300, 200))
        self.name_input.setText(product["product_name"])
        self.set_combo_value(self.category_combo, product["category_id"])
        self.description_input.setPlainText(product["description"] or "")
        self.set_combo_value(self.manufacturer_combo, product["manufacturer_id"])
        self.set_combo_value(self.supplier_combo, product["supplier_id"])
        self.price_input.setValue(float(product["price"]))
        self.unit_input.setText(product["unit_name"])
        self.quantity_input.setValue(int(product["quantity"]))
        self.discount_input.setValue(float(product["discount_percent"]))

    def set_combo_value(self, combo_box, value):
        index = combo_box.findData(value)
        if index >= 0:
            combo_box.setCurrentIndex(index)

    def load_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", "", "Изображения (*.png *.jpg *.jpeg *.bmp)"
        )
        if not file_path:
            return
        try:
            new_path = save_product_image(file_path)
            if self.current_image_path:
                remove_image_file(self.current_image_path)
            self.current_image_path = new_path
            self.photo_label.setPixmap(load_pixmap(new_path, 300, 200))
        except Exception as error:
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось загрузить изображение.\n\n{error}"
            )

    def validate_form(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Предупреждение", "Укажите наименование товара.")
            return False
        if not self.unit_input.text().strip():
            QMessageBox.warning(self, "Предупреждение", "Укажите единицу измерения.")
            return False
        if self.price_input.value() < 0:
            QMessageBox.warning(
                self, "Предупреждение", "Цена не может быть отрицательной."
            )
            return False
        if self.quantity_input.value() < 0:
            QMessageBox.warning(
                self, "Предупреждение", "Количество не может быть отрицательным."
            )
            return False
        return True

    def save_product(self):
        if not self.validate_form():
            return
        product_name = self.name_input.text().strip()
        category_id = self.category_combo.currentData()
        description = self.description_input.toPlainText().strip()
        manufacturer_id = self.manufacturer_combo.currentData()
        supplier_id = self.supplier_combo.currentData()
        price = self.price_input.value()
        unit_name = self.unit_input.text().strip()
        quantity = self.quantity_input.value()
        discount = self.discount_input.value()
        image_path = self.current_image_path
        try:
            if self.is_edit_mode:
                db.update_product(
                    (
                        self.article_label.text().strip(),
                        product_name,
                        category_id,
                        description,
                        manufacturer_id,
                        supplier_id,
                        price,
                        unit_name,
                        quantity,
                        discount,
                        image_path,
                        self.product_id,
                    )
                )
                QMessageBox.information(self, "Информация", "Товар успешно обновлён.")
            else:
                new_id = db.get_next_product_id()
                article = generate_product_article()
                db.insert_product(
                    (
                        new_id,
                        article,
                        product_name,
                        category_id,
                        description,
                        manufacturer_id,
                        supplier_id,
                        price,
                        unit_name,
                        quantity,
                        discount,
                        image_path,
                    )
                )
                QMessageBox.information(self, "Информация", "Товар успешно добавлен.")
            self.accept()
        except Exception as error:
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось сохранить товар.\n\n{error}"
            )


class OrdersWindow(QMainWindow):

    def __init__(self, user_data, products_window):
        super().__init__()
        self.user_data = user_data
        self.products_window = products_window
        self.can_edit = user_data["role_name"] == "admin"
        self.setWindowTitle("Заказы — Магазин игрушек")
        self.setMinimumSize(900, 500)
        self._build_ui()
        apply_main_style(self)
        self.load_orders()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.addWidget(HeaderWidget("Заказы", self.user_data.get("full_name", "")))
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            [
                "Артикул",
                "Статус",
                "Адрес пункта выдачи",
                "Дата заказа",
                "Дата выдачи",
                "ID",
            ]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setColumnHidden(5, True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        if self.can_edit:
            self.table.cellDoubleClicked.connect(self.open_edit_order)
        layout.addWidget(self.table)
        buttons_layout = QHBoxLayout()
        if self.can_edit:
            add_button = QPushButton("Добавить заказ")
            add_button.clicked.connect(self.open_add_order)
            buttons_layout.addWidget(add_button)
            delete_button = QPushButton("Удалить заказ")
            delete_button.clicked.connect(self.delete_selected_order)
            buttons_layout.addWidget(delete_button)
        back_button = QPushButton("Назад")
        back_button.clicked.connect(self.go_back)
        buttons_layout.addWidget(back_button)
        logout_button = QPushButton("Выход")
        logout_button.clicked.connect(self.logout)
        buttons_layout.addWidget(logout_button)
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

    def load_orders(self):
        try:
            orders = db.fetch_orders()
        except Exception as error:
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось загрузить заказы.\n\n{error}"
            )
            return
        self.table.setRowCount(len(orders))
        for row_index, order in enumerate(orders):
            issue_date = ""
            if order["issue_date"]:
                issue_date = order["issue_date"].strftime("%d.%m.%Y")
            values = [
                order["article"],
                order["status_name"],
                order["pickup_address"],
                order["order_date"].strftime("%d.%m.%Y"),
                issue_date,
                str(order["order_id"]),
            ]
            for column_index, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row_index, column_index, item)

    def open_add_order(self):
        dialog = OrderEditDialog(None, self)
        if dialog.exec():
            self.load_orders()

    def open_edit_order(self, row, column):
        order_id = int(self.table.item(row, 5).text())
        dialog = OrderEditDialog(order_id, self)
        if dialog.exec():
            self.load_orders()

    def delete_selected_order(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(
                self, "Предупреждение", "Выберите заказ в таблице для удаления."
            )
            return
        row = selected_rows[0].row()
        order_id = int(self.table.item(row, 5).text())
        article = self.table.item(row, 0).text()
        answer = QMessageBox.question(
            self,
            "Подтверждение",
            f"Вы действительно хотите удалить заказ «{article}»?\nЭто действие необратимо.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            db.delete_order(order_id)
            QMessageBox.information(self, "Информация", "Заказ успешно удалён.")
            self.load_orders()
        except Exception as error:
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось удалить заказ.\n\n{error}"
            )

    def go_back(self):
        self.close()
        self.products_window.show()

    def logout(self):
        self.products_window.close()
        self.close()
        self.products_window.login_window.show_login_again()


class OrderEditDialog(QDialog):

    def __init__(self, order_id, parent_window):
        super().__init__(parent_window)
        self.order_id = order_id
        self.parent_window = parent_window
        self.is_edit_mode = order_id is not None
        title = "Редактирование заказа" if self.is_edit_mode else "Добавление заказа"
        self.setWindowTitle(f"{title} — Магазин игрушек")
        self.setMinimumSize(480, 360)
        self._build_ui()
        apply_main_style(self)
        if self.is_edit_mode:
            self.load_order_data()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(
            HeaderWidget(
                "Редактирование заказа" if self.is_edit_mode else "Добавление заказа",
                self.parent_window.user_data.get("full_name", ""),
            )
        )
        form_layout = QFormLayout()
        self.article_input = QLineEdit()
        form_layout.addRow("Артикул:", self.article_input)
        self.status_combo = QComboBox()
        for status in db.fetch_order_statuses():
            self.status_combo.addItem(status["status_name"], status["status_id"])
        form_layout.addRow("Статус заказа:", self.status_combo)
        self.pickup_combo = QComboBox()
        for point in db.fetch_pickup_points():
            self.pickup_combo.addItem(point["address"], point["pickup_point_id"])
        form_layout.addRow("Адрес пункта выдачи:", self.pickup_combo)
        self.order_date_input = QDateEdit()
        self.order_date_input.setCalendarPopup(True)
        self.order_date_input.setDate(QDate.currentDate())
        self.order_date_input.setDisplayFormat("dd.MM.yyyy")
        form_layout.addRow("Дата заказа:", self.order_date_input)
        self.issue_date_checkbox = QCheckBox("Указать дату выдачи")
        form_layout.addRow("", self.issue_date_checkbox)
        self.issue_date_input = QDateEdit()
        self.issue_date_input.setCalendarPopup(True)
        self.issue_date_input.setDate(QDate.currentDate())
        self.issue_date_input.setDisplayFormat("dd.MM.yyyy")
        self.issue_date_input.setEnabled(False)
        self.issue_date_checkbox.toggled.connect(self.issue_date_input.setEnabled)
        form_layout.addRow("Дата выдачи:", self.issue_date_input)
        layout.addLayout(form_layout)
        buttons_layout = QHBoxLayout()
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_order)
        buttons_layout.addWidget(save_button)
        back_button = QPushButton("Назад")
        back_button.clicked.connect(self.reject)
        buttons_layout.addWidget(back_button)
        layout.addLayout(buttons_layout)

    def load_order_data(self):
        try:
            order = db.fetch_order_by_id(self.order_id)
        except Exception as error:
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось загрузить данные заказа.\n\n{error}"
            )
            self.reject()
            return
        if not order:
            QMessageBox.warning(self, "Ошибка", "Заказ не найден в базе данных.")
            self.reject()
            return
        self.article_input.setText(str(order["article"]))
        index = self.status_combo.findData(order["status_id"])
        if index >= 0:
            self.status_combo.setCurrentIndex(index)
        pickup_index = self.pickup_combo.findData(order["pickup_point_id"])
        if pickup_index >= 0:
            self.pickup_combo.setCurrentIndex(pickup_index)
        self.order_date_input.setDate(QDate(order["order_date"]))
        if order["issue_date"]:
            self.issue_date_checkbox.setChecked(True)
            self.issue_date_input.setDate(QDate(order["issue_date"]))
        else:
            self.issue_date_checkbox.setChecked(False)

    def validate_form(self):
        if not self.article_input.text().strip():
            QMessageBox.warning(self, "Предупреждение", "Укажите артикул заказа.")
            return False
        if self.pickup_combo.currentData() is None:
            QMessageBox.warning(
                self, "Предупреждение", "Выберите адрес пункта выдачи."
            )
            return False
        return True

    def get_issue_date(self):
        if not self.issue_date_checkbox.isChecked():
            return None
        return self.issue_date_input.date().toPyDate()

    def save_order(self):
        if not self.validate_form():
            return
        article = self.article_input.text().strip()
        status_id = self.status_combo.currentData()
        pickup_point_id = self.pickup_combo.currentData()
        order_date = self.order_date_input.date().toPyDate()
        issue_date = self.get_issue_date()
        try:
            if self.is_edit_mode:
                db.update_order(
                    (
                        article,
                        status_id,
                        pickup_point_id,
                        None,
                        order_date,
                        issue_date,
                        self.order_id,
                    )
                )
                QMessageBox.information(self, "Информация", "Заказ успешно обновлён.")
            else:
                new_id = db.get_next_order_id()
                db.insert_order(
                    (
                        new_id,
                        article,
                        status_id,
                        pickup_point_id,
                        None,
                        order_date,
                        issue_date,
                    )
                )
                QMessageBox.information(self, "Информация", "Заказ успешно добавлен.")
            self.accept()
        except Exception as error:
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось сохранить заказ.\n\n{error}"
            )


def main():
    ensure_directories()
    app = QApplication(sys.argv)
    app.setFont(MAIN_FONT)
    if os.path.exists(ICON_PATH):
        app.setWindowIcon(QIcon(ICON_PATH))
    is_connected, error_text = db.test_connection()
    if not is_connected:
        QMessageBox.critical(
            None,
            "Ошибка подключения",
            f"Не удалось подключиться к базе данных MySQL.\n\n{error_text}\n\nВыполните скрипт database.sql и проверьте настройки в db.py.",
        )
        sys.exit(1)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
