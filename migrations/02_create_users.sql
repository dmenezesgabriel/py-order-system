CREATE USER 'inventory_user'@'%' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON inventory.* TO 'inventory_user'@'%';

CREATE USER 'catalogue_user'@'%' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON catalogue.* TO 'catalogue_user'@'%';

CREATE USER 'pricing_user'@'%' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON pricing.* TO 'pricing_user'@'%';

CREATE USER 'search_product_user'@'%' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON search_product.* TO 'search_product_user'@'%';

CREATE USER 'order_user'@'%' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON order.* TO 'order_user'@'%';

FLUSH PRIVILEGES;
