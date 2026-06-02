import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "port": 3306,
    "database": "toy_shop",
    "charset": "utf8mb4",
    "autocommit": False,
}


def get_connect():
    return mysql.connector.connect(**DB_CONFIG)


def authenticate_user(login, password):
    connection = None
    cursor = None
    try:
        connection = get_connect()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT u.user_id, u.login, u.full_name, r.role_name
            FROM users u
            JOIN roles r ON u.role_id = r.role_id
            WHERE u.login = %s AND u.password = %s
        """
        cursor.execute(query, (login, password))
        return cursor.fetchone()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def fetch_categories():
    connection = None
    cursor = None
    try:
        connection = get_connect()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT category_id, category_name FROM categories ORDER BY category_name"
        )
        return cursor.fetchall()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def fetch_suppliers():
    connection = None
    cursor = None
    try:
        connection = get_connect()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT supplier_id, supplier_name FROM suppliers ORDER BY supplier_name"
        )
        return cursor.fetchall()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def fetch_manufacturers():
    connection = None
    cursor = None
    try:
        connection = get_connect()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT manufacturer_id, manufacturer_name "
            "FROM manufacturers ORDER BY manufacturer_name"
        )
        return cursor.fetchall()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def fetch_pickup_points():
    connection = None
    cursor = None
    try:
        connection = get_connect()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT pickup_point_id, address FROM pickup_points ORDER BY pickup_point_id"
        )
        return cursor.fetchall()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def fetch_order_statuses():
    connection = None
    cursor = None
    try:
        connection = get_connect()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT status_id, status_name FROM order_statuses ORDER BY status_id"
        )
        return cursor.fetchall()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def fetch_products(search_text="", supplier_id=None, sort_field="", sort_order="ASC"):
    connection = None
    cursor = None
    try:
        connection = get_connect()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT
                p.product_id,
                p.article,
                p.product_name,
                c.category_name,
                p.description,
                m.manufacturer_name,
                s.supplier_name,
                s.supplier_id,
                p.price,
                p.unit_name,
                p.quantity,
                p.discount_percent,
                p.image_path
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            JOIN manufacturers m ON p.manufacturer_id = m.manufacturer_id
            JOIN suppliers s ON p.supplier_id = s.supplier_id
            WHERE 1 = 1
        """
        params = []
        if supplier_id:
            query += " AND s.supplier_id = %s"
            params.append(supplier_id)
        if search_text:
            like_value = f"%{search_text}%"
            query += """
                AND (
                    p.article LIKE %s
                    OR p.product_name LIKE %s
                    OR c.category_name LIKE %s
                    OR p.description LIKE %s
                    OR m.manufacturer_name LIKE %s
                    OR s.supplier_name LIKE %s
                    OR p.unit_name LIKE %s
                    OR CAST(p.price AS CHAR) LIKE %s
                    OR CAST(p.quantity AS CHAR) LIKE %s
                    OR CAST(p.discount_percent AS CHAR) LIKE %s
                )
            """
            params.extend([like_value] * 10)
        allowed_sort = {"quantity": "p.quantity", "price": "p.price"}
        if sort_field in allowed_sort:
            direction = "DESC" if sort_order.upper() == "DESC" else "ASC"
            query += f" ORDER BY {allowed_sort[sort_field]} {direction}"
        else:
            query += " ORDER BY p.product_id"
        cursor.execute(query, params)
        return cursor.fetchall()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def fetch_product_by_id(product_id):
    connection = None
    cursor = None
    try:
        connection = get_connect()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT
                p.product_id,
                p.article,
                p.product_name,
                p.category_id,
                c.category_name,
                p.description,
                p.manufacturer_id,
                m.manufacturer_name,
                p.supplier_id,
                s.supplier_name,
                p.price,
                p.unit_name,
                p.quantity,
                p.discount_percent,
                p.image_path
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            JOIN manufacturers m ON p.manufacturer_id = m.manufacturer_id
            JOIN suppliers s ON p.supplier_id = s.supplier_id
            WHERE p.product_id = %s
        """
        cursor.execute(query, (product_id,))
        return cursor.fetchone()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def get_next_product_id():
    connection = None
    cursor = None
    try:
        connection = get_connect()
        cursor = connection.cursor()
        cursor.execute("SELECT COALESCE(MAX(product_id), 0) + 1 FROM products")
        result = cursor.fetchone()
        return result[0]
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def article_exists(article):
    connection = None
    cursor = None
    try:
        connection = get_connect()
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM products WHERE article = %s", (article,))
        result = cursor.fetchone()
        return result[0] > 0
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def insert_product(product_data):
    connection = None
    cursor = None
    try:
        connection = get_connect()
        cursor = connection.cursor()
        query = """
            INSERT INTO products (
                product_id, article, product_name, category_id, description,
                manufacturer_id, supplier_id, price, unit_name,
                quantity, discount_percent, image_path
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, product_data)
        connection.commit()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def update_product(product_data):
    connection = None
    cursor = None
    try:
        connection = get_connect()
        cursor = connection.cursor()
        query = """
            UPDATE products SET
                article = %s,
                product_name = %s,
                category_id = %s,
                description = %s,
                manufacturer_id = %s,
                supplier_id = %s,
                price = %s,
                unit_name = %s,
                quantity = %s,
                discount_percent = %s,
                image_path = %s
            WHERE product_id = %s
        """
        cursor.execute(query, product_data)
        connection.commit()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def delete_product(product_id):
    connection = None
    cursor = None
    try:
        connection = get_connect()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
        connection.commit()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def is_product_in_orders(product_id):
    connection = None
    cursor = None
    try:
        connection = get_connect()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM order_items WHERE product_id = %s",
            (product_id,),
        )
        result = cursor.fetchone()
        return result[0] > 0
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def fetch_orders():
    connection = None
    cursor = None
    try:
        connection = get_connect()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT
                o.order_id,
                o.article,
                os.status_name,
                o.status_id,
                pp.address AS pickup_address,
                o.pickup_point_id,
                o.client_name,
                o.order_date,
                o.issue_date
            FROM orders o
            JOIN order_statuses os ON o.status_id = os.status_id
            JOIN pickup_points pp ON o.pickup_point_id = pp.pickup_point_id
            ORDER BY o.order_id
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def fetch_order_by_id(order_id):
    connection = None
    cursor = None
    try:
        connection = get_connect()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT
                order_id, article, status_id, pickup_point_id,
                client_name, order_date, issue_date
            FROM orders
            WHERE order_id = %s
        """
        cursor.execute(query, (order_id,))
        return cursor.fetchone()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def get_next_order_id():
    connection = None
    cursor = None
    try:
        connection = get_connect()
        cursor = connection.cursor()
        cursor.execute("SELECT COALESCE(MAX(order_id), 0) + 1 FROM orders")
        result = cursor.fetchone()
        return result[0]
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def insert_order(order_data):
    connection = None
    cursor = None
    try:
        connection = get_connect()
        cursor = connection.cursor()
        query = """
            INSERT INTO orders (
                order_id, article, status_id, pickup_point_id,
                client_name, order_date, issue_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, order_data)
        connection.commit()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def update_order(order_data):
    connection = None
    cursor = None
    try:
        connection = get_connect()
        cursor = connection.cursor()
        query = """
            UPDATE orders SET
                article = %s,
                status_id = %s,
                pickup_point_id = %s,
                client_name = %s,
                order_date = %s,
                issue_date = %s
            WHERE order_id = %s
        """
        cursor.execute(query, order_data)
        connection.commit()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def delete_order(order_id):
    connection = None
    cursor = None
    try:
        connection = get_connect()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
        connection.commit()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def test_connection():
    try:
        connection = get_connect()
        connection.close()
        return True, ""
    except Error as error:
        return False, str(error)
