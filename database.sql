DROP DATABASE IF EXISTS toy_shop;
CREATE DATABASE toy_shop CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE toy_shop;

CREATE TABLE roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    login VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    role_id INT NOT NULL,
    CONSTRAINT fk_users_role FOREIGN KEY (role_id) REFERENCES roles(role_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(150) NOT NULL UNIQUE
);

CREATE TABLE manufacturers (
    manufacturer_id INT AUTO_INCREMENT PRIMARY KEY,
    manufacturer_name VARCHAR(150) NOT NULL UNIQUE
);

CREATE TABLE suppliers (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_name VARCHAR(150) NOT NULL UNIQUE
);

CREATE TABLE pickup_points (
    pickup_point_id INT AUTO_INCREMENT PRIMARY KEY,
    address VARCHAR(300) NOT NULL UNIQUE
);

CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    article VARCHAR(20) NOT NULL UNIQUE,
    product_name VARCHAR(500) NOT NULL,
    category_id INT NOT NULL,
    description TEXT,
    manufacturer_id INT NOT NULL,
    supplier_id INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    unit_name VARCHAR(20) NOT NULL DEFAULT 'шт.',
    quantity INT NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    discount_percent DECIMAL(5, 2) NOT NULL DEFAULT 0 CHECK (discount_percent >= 0),
    image_path VARCHAR(500),
    CONSTRAINT fk_products_category FOREIGN KEY (category_id) REFERENCES categories(category_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_products_manufacturer FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(manufacturer_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_products_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE order_statuses (
    status_id INT AUTO_INCREMENT PRIMARY KEY,
    status_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    article VARCHAR(50) NOT NULL UNIQUE,
    status_id INT NOT NULL,
    pickup_point_id INT NOT NULL,
    client_name VARCHAR(150),
    order_date DATE NOT NULL,
    issue_date DATE,
    CONSTRAINT fk_orders_status FOREIGN KEY (status_id) REFERENCES order_statuses(status_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_orders_pickup FOREIGN KEY (pickup_point_id) REFERENCES pickup_points(pickup_point_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1 CHECK (quantity > 0),
    CONSTRAINT fk_order_items_order FOREIGN KEY (order_id) REFERENCES orders(order_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_order_items_product FOREIGN KEY (product_id) REFERENCES products(product_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

INSERT INTO roles (role_name) VALUES ('client'), ('manager'), ('admin');

INSERT INTO users (login, password, full_name, role_id) VALUES ('94d5ous@gmail.com', 'uzWC67', 'Ворсин Петр Евгеньевич', 3);
INSERT INTO users (login, password, full_name, role_id) VALUES ('uth4iz@mail.com', '2L6KZG', 'Старикова Елена Павловна', 3);
INSERT INTO users (login, password, full_name, role_id) VALUES ('yzls62@outlook.com', 'JlFRCZ', 'Одинцов Серафим Артёмович', 3);
INSERT INTO users (login, password, full_name, role_id) VALUES ('1diph5e@tutanota.com', '8ntwUp', 'Михайлюк Анна Вячеславовна', 2);
INSERT INTO users (login, password, full_name, role_id) VALUES ('tjde7c@yahoo.com', 'YOyhfR', 'Ситдикова Елена Анатольевна', 2);
INSERT INTO users (login, password, full_name, role_id) VALUES ('wpmrc3do@tutanota.com', 'RSbvHv', 'Никифорова Весения Николаевна', 2);
INSERT INTO users (login, password, full_name, role_id) VALUES ('5d4zbu@tutanota.com', 'rwVDh9', 'Степанов Михаил Артёмович', 1);
INSERT INTO users (login, password, full_name, role_id) VALUES ('ptec8ym@yahoo.com', 'LdNyos', 'Ворсин Петр Евгеньевич', 1);
INSERT INTO users (login, password, full_name, role_id) VALUES ('1qz4kw@mail.com', 'gynQMT', 'Старикова Елена Павловна', 1);
INSERT INTO users (login, password, full_name, role_id) VALUES ('4np6se@mail.com', 'AtnDjr', 'Сазонов Руслан Германович', 1);

INSERT INTO categories (category_name) VALUES ('Детский музыкальный инструмент');
INSERT INTO categories (category_name) VALUES ('Игровой набор');
INSERT INTO categories (category_name) VALUES ('Конструктор');
INSERT INTO categories (category_name) VALUES ('Машинка');

INSERT INTO manufacturers (manufacturer_name) VALUES ('ABSпластик');
INSERT INTO manufacturers (manufacturer_name) VALUES ('BambiniFelici');
INSERT INTO manufacturers (manufacturer_name) VALUES ('Junion');

INSERT INTO suppliers (supplier_name) VALUES ('CHILITOY');
INSERT INTO suppliers (supplier_name) VALUES ('Knauf');
INSERT INTO suppliers (supplier_name) VALUES ('Pikeshop');
INSERT INTO suppliers (supplier_name) VALUES ('Playbig');
INSERT INTO suppliers (supplier_name) VALUES ('Vinylon');

INSERT INTO pickup_points (address) VALUES ('420151, г. Лесной, ул. Вишневая, 32');
INSERT INTO pickup_points (address) VALUES ('125061, г. Лесной, ул. Подгорная, 8');
INSERT INTO pickup_points (address) VALUES ('630370, г. Лесной, ул. Шоссейная, 24');
INSERT INTO pickup_points (address) VALUES ('400562, г. Лесной, ул. Зеленая, 32');
INSERT INTO pickup_points (address) VALUES ('614510, г. Лесной, ул. Маяковского, 47');
INSERT INTO pickup_points (address) VALUES ('410542, г. Лесной, ул. Светлая, 46');
INSERT INTO pickup_points (address) VALUES ('620839, г. Лесной, ул. Цветочная, 8');
INSERT INTO pickup_points (address) VALUES ('443890, г. Лесной, ул. Коммунистическая, 1');
INSERT INTO pickup_points (address) VALUES ('603379, г. Лесной, ул. Спортивная, 46');
INSERT INTO pickup_points (address) VALUES ('603721, г. Лесной, ул. Гоголя, 41');
INSERT INTO pickup_points (address) VALUES ('410172, г. Лесной, ул. Северная, 13');
INSERT INTO pickup_points (address) VALUES ('614611, г. Лесной, ул. Молодежная, 50');
INSERT INTO pickup_points (address) VALUES ('454311, г.Лесной, ул. Новая, 19');
INSERT INTO pickup_points (address) VALUES ('660007, г.Лесной, ул. Октябрьская, 19');
INSERT INTO pickup_points (address) VALUES ('603036, г. Лесной, ул. Садовая, 4');
INSERT INTO pickup_points (address) VALUES ('394060, г.Лесной, ул. Фрунзе, 43');
INSERT INTO pickup_points (address) VALUES ('410661, г. Лесной, ул. Школьная, 50');
INSERT INTO pickup_points (address) VALUES ('625590, г. Лесной, ул. Коммунистическая, 20');
INSERT INTO pickup_points (address) VALUES ('625683, г. Лесной, ул. 8 Марта');
INSERT INTO pickup_points (address) VALUES ('450983, г.Лесной, ул. Комсомольская, 26');
INSERT INTO pickup_points (address) VALUES ('394782, г. Лесной, ул. Чехова, 3');
INSERT INTO pickup_points (address) VALUES ('603002, г. Лесной, ул. Дзержинского, 28');
INSERT INTO pickup_points (address) VALUES ('450558, г. Лесной, ул. Набережная, 30');
INSERT INTO pickup_points (address) VALUES ('344288, г. Лесной, ул. Чехова, 1');
INSERT INTO pickup_points (address) VALUES ('614164, г.Лесной,  ул. Степная, 30');
INSERT INTO pickup_points (address) VALUES ('394242, г. Лесной, ул. Коммунистическая, 43');
INSERT INTO pickup_points (address) VALUES ('660540, г. Лесной, ул. Солнечная, 25');
INSERT INTO pickup_points (address) VALUES ('125837, г. Лесной, ул. Шоссейная, 40');
INSERT INTO pickup_points (address) VALUES ('125703, г. Лесной, ул. Партизанская, 49');
INSERT INTO pickup_points (address) VALUES ('625283, г. Лесной, ул. Победы, 46');
INSERT INTO pickup_points (address) VALUES ('614753, г. Лесной, ул. Полевая, 35');
INSERT INTO pickup_points (address) VALUES ('426030, г. Лесной, ул. Маяковского, 44');
INSERT INTO pickup_points (address) VALUES ('450375, г. Лесной ул. Клубная, 44');
INSERT INTO pickup_points (address) VALUES ('625560, г. Лесной, ул. Некрасова, 12');
INSERT INTO pickup_points (address) VALUES ('630201, г. Лесной, ул. Комсомольская, 17');
INSERT INTO pickup_points (address) VALUES ('190949, г. Лесной, ул. Мичурина, 26');

INSERT INTO products (product_id, article, product_name, category_id, description, manufacturer_id, supplier_id, price, unit_name, quantity, discount_percent, image_path) VALUES (1, 'PMEZMH', 'Детский игровой набор машинок Щенячий патруль / Dogs mini . 9 героев + 9 инерфионных машинок', 2, 'Детский набор машинок с героями мультсериала «Щенячий патруль» подойдет как для мальчиков, так и для девочек. В детский набор входит 9 фигурок щенков спасателей. ', 1, 3, 1414, 'шт.', 50, 22, 'images/1.JPG');
INSERT INTO products (product_id, article, product_name, category_id, description, manufacturer_id, supplier_id, price, unit_name, quantity, discount_percent, image_path) VALUES (2, 'BPV4MM', 'Конструктор Гарри Поттер Сова Букля 630 деталей совместим с lego harry potter, лего совместимый)', 3, 'Коллекционная модель Букля состоит из множества потрясающих элементов, а также специального механизма внутри. С его помощью можно плавно поднимать-опускать крылья птицы.', 1, 4, 771, 'шт.', 26, 15, 'images/2.JPG');
INSERT INTO products (product_id, article, product_name, category_id, description, manufacturer_id, supplier_id, price, unit_name, quantity, discount_percent, image_path) VALUES (3, 'JVL42J', 'Музыкальные инструменты для детей, ксилофон, барабаны, развивающие игрушки, игрушки для детей', 1, 'Откройте мир музыки для вашего ребенка с этой уникальной игрушкой! Это многофункциональное музыкальное чудо объединяет в себе всё, что нужно для творческого развития.', 2, 4, 2750, 'шт.', 0, 15, 'images/3.JPG');
INSERT INTO products (product_id, article, product_name, category_id, description, manufacturer_id, supplier_id, price, unit_name, quantity, discount_percent, image_path) VALUES (4, 'F895RB', 'Машинка игрушка диско шар светящаяся музыкальная', 4, 'Светящаяся музыкальная машина с диско шаром переливается разными цветами, играет ритмичные мелодии, объезжает препятствия и крутится, поэтому с ней точно не будет скучно.', 1, 2, 368, 'шт.', 7, 6, 'images/4.JPG');
INSERT INTO products (product_id, article, product_name, category_id, description, manufacturer_id, supplier_id, price, unit_name, quantity, discount_percent, image_path) VALUES (5, '3XBOTN', 'Игровой набор Hot Wheels Action Loop Cyclone Challenge Track, с машинкой и удобным хранением, HTK16', 2, 'Игровой набор Hot Wheels Action Loop Cyclone Challenge Track - это уникальная игра, которая позволит вам испытать себя и своих друзей в скорости и ловкости. Этот набор состоит из металлической дорожки с циклоном, которая создает потрясающий эффект и добавляет дополнительную сложность в игру.', 2, 2, 3426, 'шт.', 21, 10, 'images/5.JPG');
INSERT INTO products (product_id, article, product_name, category_id, description, manufacturer_id, supplier_id, price, unit_name, quantity, discount_percent, image_path) VALUES (6, '3L7RCZ', 'Игровой набор с деревянными машинками Стройплощадка Кран-Паркс, Junion', 2, 'Игровой набор «Стройплощадка Кран-Паркс Junion» — это большая игрушечная парковка с деревянными машинками и настоящим подъёмным краном, придуманная в Яндексе настоящими родителями.', 3, 2, 7400, 'шт.', 0, 15, 'images/6.JPG');
INSERT INTO products (product_id, article, product_name, category_id, description, manufacturer_id, supplier_id, price, unit_name, quantity, discount_percent, image_path) VALUES (7, 'S72AM3', 'Синтезатор детский с микрофоном 61 клавиша', 1, 'Откройте для ребенка дверь в мир музыки с детским синтезатором! Этот компактный инструмент с микрофоном станет верным другом для юных музыкантов, помогая им развивать творческий потенциал и получать удовольствие от игры.', 3, 1, 1749, 'шт.', 35, 10, 'images/7.JPG');
INSERT INTO products (product_id, article, product_name, category_id, description, manufacturer_id, supplier_id, price, unit_name, quantity, discount_percent, image_path) VALUES (8, '2G3280', 'Деревянный игровой набор JUNION Стройплощадка "Кран-Паркс" с подъёмным, строительным краном и машинками, 18 предметов, подвижные элементы', 2, 'Игровой набор «Стройплощадка Кран-Паркс Junion» — это большая игрушечная парковка с деревянными машинками и настоящим подъёмным краном, придуманная в Яндексе настоящими родителями.', 3, 5, 1624, 'шт.', 20, 9, 'images/8.JPG');
INSERT INTO products (product_id, article, product_name, category_id, description, manufacturer_id, supplier_id, price, unit_name, quantity, discount_percent, image_path) VALUES (9, 'MIO8YV', 'Музыкальная игрушка интерактивная Пульт, детский прорезыватель для малышей', 1, 'Музыкальная игрушка интерактивная Пульт, детский прорезыватель для малышей', 2, 5, 305, 'шт.', 31, 9, 'images/9.JPG');
INSERT INTO products (product_id, article, product_name, category_id, description, manufacturer_id, supplier_id, price, unit_name, quantity, discount_percent, image_path) VALUES (10, 'UER2QD', 'Большой набор опытов и экспериментов для детей 14 в 1', 2, 'Большой набор опытов и экспериментов для детей 14 в 1', 2, 5, 2506, 'шт.', 27, 8, 'images/10.JPG');

INSERT INTO order_statuses (status_name) VALUES ('Завершен');
INSERT INTO order_statuses (status_name) VALUES ('Новый');

INSERT INTO orders (order_id, article, status_id, pickup_point_id, client_name, order_date, issue_date) VALUES (1, '901', 1, 1, 'Степанов Михаил Артёмович', '2025-02-27', '2025-04-20');
INSERT INTO orders (order_id, article, status_id, pickup_point_id, client_name, order_date, issue_date) VALUES (2, '902', 1, 11, 'Ворсин Петр Евгеньевич', '2024-09-28', '2025-04-21');
INSERT INTO orders (order_id, article, status_id, pickup_point_id, client_name, order_date, issue_date) VALUES (3, '903', 1, 2, 'Старикова Елена Павловна', '2025-03-21', '2025-04-22');
INSERT INTO orders (order_id, article, status_id, pickup_point_id, client_name, order_date, issue_date) VALUES (4, '904', 1, 11, 'Сазонов Руслан Германович', '2025-02-20', '2025-04-23');
INSERT INTO orders (order_id, article, status_id, pickup_point_id, client_name, order_date, issue_date) VALUES (5, '905', 1, 2, 'Степанов Михаил Артёмович', '2025-03-17', '2025-04-24');
INSERT INTO orders (order_id, article, status_id, pickup_point_id, client_name, order_date, issue_date) VALUES (6, '906', 1, 15, 'Ворсин Петр Евгеньевич', '2025-03-01', '2025-04-25');
INSERT INTO orders (order_id, article, status_id, pickup_point_id, client_name, order_date, issue_date) VALUES (7, '907', 1, 3, 'Старикова Елена Павловна', '2025-03-01', '2025-04-26');
INSERT INTO orders (order_id, article, status_id, pickup_point_id, client_name, order_date, issue_date) VALUES (8, '908', 2, 19, 'Сазонов Руслан Германович', '2025-03-31', '2025-04-27');
INSERT INTO orders (order_id, article, status_id, pickup_point_id, client_name, order_date, issue_date) VALUES (9, '909', 2, 5, 'Старикова Елена Павловна', '2025-04-02', '2025-04-28');
INSERT INTO orders (order_id, article, status_id, pickup_point_id, client_name, order_date, issue_date) VALUES (10, '910', 2, 19, 'Сазонов Руслан Германович', '2025-04-03', '2025-04-29');

INSERT INTO order_items (order_id, product_id, quantity) VALUES (1, 1, 2);
INSERT INTO order_items (order_id, product_id, quantity) VALUES (1, 2, 2);
INSERT INTO order_items (order_id, product_id, quantity) VALUES (2, 3, 1);
INSERT INTO order_items (order_id, product_id, quantity) VALUES (2, 4, 1);
INSERT INTO order_items (order_id, product_id, quantity) VALUES (3, 5, 10);
INSERT INTO order_items (order_id, product_id, quantity) VALUES (3, 6, 10);
INSERT INTO order_items (order_id, product_id, quantity) VALUES (4, 7, 5);
INSERT INTO order_items (order_id, product_id, quantity) VALUES (4, 8, 4);
INSERT INTO order_items (order_id, product_id, quantity) VALUES (5, 9, 2);
INSERT INTO order_items (order_id, product_id, quantity) VALUES (5, 10, 2);
INSERT INTO order_items (order_id, product_id, quantity) VALUES (6, 1, 2);
INSERT INTO order_items (order_id, product_id, quantity) VALUES (6, 2, 2);
INSERT INTO order_items (order_id, product_id, quantity) VALUES (7, 3, 1);
INSERT INTO order_items (order_id, product_id, quantity) VALUES (7, 4, 1);
INSERT INTO order_items (order_id, product_id, quantity) VALUES (8, 5, 10);
INSERT INTO order_items (order_id, product_id, quantity) VALUES (8, 6, 10);
INSERT INTO order_items (order_id, product_id, quantity) VALUES (9, 7, 5);
INSERT INTO order_items (order_id, product_id, quantity) VALUES (9, 8, 4);
INSERT INTO order_items (order_id, product_id, quantity) VALUES (10, 9, 2);
INSERT INTO order_items (order_id, product_id, quantity) VALUES (10, 10, 2);
