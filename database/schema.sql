-- =====================================================
-- CS340 Project: University Student Marketplace
-- File: schema.sql  (creates the database + all tables)
-- Requires MySQL 8.0.16+ (for CHECK constraints)
-- =====================================================

DROP DATABASE IF EXISTS uni_market;
CREATE DATABASE uni_market
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
USE uni_market;

-- -----------------------------------------------------
-- 1) users: students and admins
-- -----------------------------------------------------
CREATE TABLE users (
    user_id       INT AUTO_INCREMENT PRIMARY KEY,
    full_name     VARCHAR(100) NOT NULL,
    email         VARCHAR(100) NOT NULL UNIQUE,      -- no two users with same email
    password_hash VARCHAR(255) NOT NULL,             -- never store plain passwords
    phone         VARCHAR(20),
    role          ENUM('user', 'seller', 'admin') NOT NULL DEFAULT 'user',
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------
-- 2) categories: Books, Stationery, Tutoring, ...
-- -----------------------------------------------------
CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(50) NOT NULL UNIQUE
);

-- -----------------------------------------------------
-- 3) listings: items or services posted by sellers
-- -----------------------------------------------------
CREATE TABLE listings (
    listing_id  INT AUTO_INCREMENT PRIMARY KEY,
    seller_id   INT NOT NULL,
    category_id INT NULL,                            -- NULL allowed (SET NULL below)
    title       VARCHAR(100) NOT NULL,
    description TEXT,
    price       DECIMAL(8,2) NOT NULL,
    item_type   ENUM('product', 'service') NOT NULL,
    status      ENUM('available', 'sold') NOT NULL DEFAULT 'available',
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_listing_price CHECK (price >= 0),

    -- If the seller is deleted, delete all his listings
    CONSTRAINT fk_listing_seller
        FOREIGN KEY (seller_id) REFERENCES users(user_id)
        ON DELETE CASCADE,

    -- If the category is deleted, keep the listing but set category to NULL
    CONSTRAINT fk_listing_category
        FOREIGN KEY (category_id) REFERENCES categories(category_id)
        ON DELETE SET NULL
);

-- -----------------------------------------------------
-- 4) orders: a user requests a listing
-- -----------------------------------------------------
CREATE TABLE orders (
    order_id   INT AUTO_INCREMENT PRIMARY KEY,
    buyer_id   INT NOT NULL,
    listing_id INT NOT NULL,
    status     ENUM('pending', 'accepted', 'completed', 'cancelled')
               NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- If the buyer is deleted, delete his orders
    CONSTRAINT fk_order_buyer
        FOREIGN KEY (buyer_id) REFERENCES users(user_id)
        ON DELETE CASCADE,

    -- A listing that has orders cannot be deleted (protects order history)
    CONSTRAINT fk_order_listing
        FOREIGN KEY (listing_id) REFERENCES listings(listing_id)
        ON DELETE RESTRICT
);