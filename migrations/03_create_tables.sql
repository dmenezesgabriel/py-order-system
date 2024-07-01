USE catalogue;

CREATE TABLE Inventory (
    id INT PRIMARY KEY AUTO_INCREMENT,
    in_stock INT NOT NULL,
    reserved INT DEFAULT 0
    created_at DATE NOT NULL
    updated_at DATE NOT NULL
);

CREATE TABLE Price (
    id INT PRIMARY KEY AUTO_INCREMENT,
    priceList FLOAT NOT NULL,
    discountPrice FLOAT NOT NULL
    created_at DATE NOT NULL
    updated_at DATE NOT NULL
);

CREATE TABLE Category (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    created_at DATE NOT NULL
    updated_at DATE NOT NULL
)

CREATE TABLE Product (
    id INT PRIMARY KEY AUTO_INCREMENT,
    version INT NOT NULL,
    sku VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    imageUrl VARCHAR(255) NOT NULL,
    category_id INT NOT NULL,
    price_id INT NOT NULL,
    inventory_id INT NOT NULL,
    created_at DATE NOT NULL
    updated_at DATE NOT NULL
    FOREIGN KEY (category_id) REFERENCES Category(id)
    FOREIGN KEY (price_id) REFERENCES Price(id),
    FOREIGN KEY (inventory_id) REFERENCES Inventory(id)
);

CREATE TABLE Order (
    id INT PRIMARY KEY AUTO_INCREMENT,
    total_price FLOAT NOT NULL
    customer_id INT NOT NULL,
    created_at DATE NOT NULL
    updated_at DATE NOT NULL
    FOREIGN KEY (customer_id) REFERENCES Customer(id),
)

CREATE TABLE OrderItem (
    id INT PRIMARY KEY AUTO_INCREMENT,
    version INT NOT NULL,
    order_id INT,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price_id INT NOT NULL,
    created_at DATE NOT NULL
    updated_at DATE NOT NULL
    FOREIGN KEY (order_id) REFERENCES Order(id),
    FOREIGN KEY (product_id) REFERENCES Product(id),
    FOREIGN KEY (price_id) REFERENCES Price(id),
    UNIQUE (order_id, product_id)
);



CREATE TABLE Payment (
    id INT PRIMARY KEY AUTO_INCREMENT,
    payment_method VARCHAR(255) NOT NULL,
    payment_status VARCHAR(255) NOT NULL,
    amount FLOAT NOT NULL,
    order_id INT NOT NULL,
    created_at DATE NOT NULL
    updated_at DATE NOT NULL
    FOREIGN KEY (order_id) REFERENCES Order(id),
)

CREATE TABLE OrderStatus (
    id INT PRIMARY KEY AUTO_INCREMENT,
    status VARCHAR(255) NOT NULL,
    order_id INT NOT NULL,
    created_at DATE NOT NULL
    updated_at DATE NOT NULL
    FOREIGN KEY (order_id) REFERENCES Order(id),
)

CREATE TABLE Customer (
    id INT PRIMARY KEY AUTO_INCREMENT,
    first_name
    last_name
    email
    password
    address
    phone_number
    created_at DATE NOT NULL
    updated_at DATE NOT NULL
)

CREATE TABLE Shipment (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    customer_id INT NOT NULL,
    created_at DATE NOT NULL
    updated_at DATE NOT NULL
    FOREIGN KEY (order_id) REFERENCES Order(id),
    FOREIGN KEY (customer_id) REFERENCES Customer(id),

)

CREATE TABLE Cart (
  id INT PRIMARY KEY AUTO_INCREMENT,
  quantity INT NOT NULL,
  product_id INT NOT NULL,
  customer_id INT NOT NULL,
  created_at DATE NOT NULL
  updated_at DATE NOT NULL
  FOREIGN KEY (product_id) REFERENCES Product(id),
  FOREIGN KEY (customer_id) REFERENCES Customer(id),
)

CREATE TABLE Wishlist (
  id INT PRIMARY KEY AUTO_INCREMENT,
  product_id INT NOT NULL,
  customer_id INT NOT NULL,
  created_at DATE NOT NULL
  updated_at DATE NOT NULL
  FOREIGN KEY (product_id) REFERENCES Product(id),
  FOREIGN KEY (customer_id) REFERENCES Customer(id),
)
