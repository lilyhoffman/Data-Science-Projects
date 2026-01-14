DROP DATABASE IF EXISTS financial_cleaner_db;
-- Creating the database, which will be called pack_track --
CREATE DATABASE financial_cleaner_db;

-- Using the database we just made (financial_cleaner_db) --
USE financial_cleaner_db;

CREATE TABLE users (
    customerId INT AUTO_INCREMENT PRIMARY KEY,
    firstName VARCHAR(50),
    lastName VARCHAR(50),
    age INT,
    city VARCHAR(50),
    email VARCHAR(75) UNIQUE NOT NULL,
    accountBalance INT,
    creditLimit INT,
    creditCardBalance INT
    );