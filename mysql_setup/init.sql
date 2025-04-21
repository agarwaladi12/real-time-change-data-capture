-- Create Inventory Database and Products Table

CREATE DATABASE IF NOT EXISTS inventory;

USE inventory;

CREATE TABLE IF NOT EXISTS products (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    price DECIMAL(10,2)
);

-- Insert sample records
INSERT INTO products (id, name, description, price) VALUES
(1, 'Laptop', 'High-performance laptop', 999.99),
(2, 'Mouse', 'Wireless ergonomic mouse', 49.99);
