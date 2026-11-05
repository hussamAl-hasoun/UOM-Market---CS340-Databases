-- =====================================================
-- File: moderation.sql  (admin moderation features)
-- Run it ONCE in MySQL Workbench, after schema.sql and seed.sql.
-- (If you ever rebuild: schema.sql -> seed.sql -> moderation.sql)
-- =====================================================

USE uni_market;

-- 1) users.is_active: the admin can suspend a student
ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT 1;

-- 2) moderation_log: a record of every listing the admin removes
--    ON DELETE SET NULL keeps the log row even if a user is deleted later.
--    listing_title is copied, because the listing itself gets deleted.
CREATE TABLE moderation_log (
    log_id         INT AUTO_INCREMENT PRIMARY KEY,
    admin_id       INT NULL,
    seller_id      INT NULL,
    listing_title  VARCHAR(100) NOT NULL,
    reason         VARCHAR(255) NOT NULL,
    orders_removed INT NOT NULL DEFAULT 0,
    created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_log_admin
        FOREIGN KEY (admin_id)  REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_log_seller
        FOREIGN KEY (seller_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- 3) VIEW: everything the admin needs to know about each listing
CREATE OR REPLACE VIEW admin_listings_overview AS
SELECT l.listing_id, l.title, l.description, l.price, l.item_type, l.status, l.created_at,
       c.name      AS category,
       u.user_id   AS seller_id,
       u.full_name AS seller,
       u.email     AS seller_email,
       u.phone     AS seller_phone,
       (SELECT COUNT(*) FROM orders o WHERE o.listing_id = l.listing_id) AS orders_count
FROM listings l
JOIN users u           ON l.seller_id = u.user_id
LEFT JOIN categories c ON l.category_id = c.category_id;

-- 4) VIEW: everything the admin needs to know about each user
CREATE OR REPLACE VIEW admin_users_overview AS
SELECT u.user_id, u.full_name, u.email, u.phone, u.role, u.is_active, u.created_at,
       (SELECT COUNT(*) FROM listings l WHERE l.seller_id = u.user_id) AS listings_count,
       (SELECT COUNT(*) FROM orders   o WHERE o.buyer_id  = u.user_id) AS orders_count
FROM users u;
