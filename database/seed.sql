-- =====================================================
-- File: seed.sql  (sample data for testing)
-- Run AFTER schema.sql
-- All sample users have the password: 123456
-- =====================================================

USE uni_market;

-- Categories
INSERT INTO categories (name) VALUES
    ('Books'),
    ('Stationery'),
    ('Electronics'),
    ('Tutoring'),
    ('Printing & Design');

-- Users (1 admin, 2 sellers, 2 normal users)
INSERT INTO users (full_name, email, password_hash, phone, role) VALUES
    ('Admin',          'admin@student.edu.sa',  'pbkdf2:sha256:1000000$mxbE2jpe0CwIA88d$c40dc085b7dd368df1eb4193bd0df8e962663cbe7bbdee828187a787130f39bf', '0500000000', 'admin'),
    ('Ahmed Ali',      'ahmed@student.edu.sa',  'pbkdf2:sha256:1000000$mxbE2jpe0CwIA88d$c40dc085b7dd368df1eb4193bd0df8e962663cbe7bbdee828187a787130f39bf', '0501111111', 'seller'),
    ('Khaled Omar',    'khaled@student.edu.sa', 'pbkdf2:sha256:1000000$mxbE2jpe0CwIA88d$c40dc085b7dd368df1eb4193bd0df8e962663cbe7bbdee828187a787130f39bf', '0502222222', 'seller'),
    ('Sara Nasser',    'sara@student.edu.sa',   'pbkdf2:sha256:1000000$mxbE2jpe0CwIA88d$c40dc085b7dd368df1eb4193bd0df8e962663cbe7bbdee828187a787130f39bf', '0503333333', 'user'),
    ('Fahad Saad',     'fahad@student.edu.sa',  'pbkdf2:sha256:1000000$mxbE2jpe0CwIA88d$c40dc085b7dd368df1eb4193bd0df8e962663cbe7bbdee828187a787130f39bf', '0504444444', 'user');

-- Listings (seller_id: 2 = Ahmed, 3 = Khaled)
INSERT INTO listings (seller_id, category_id, title, description, price, item_type) VALUES
    (2, 1, 'Database Systems Book',       'Elmasri & Navathe, like new',            40.00, 'product'),
    (2, 1, 'Data Structures Book',        'Some highlights inside',                 25.00, 'product'),
    (2, 4, 'Programming Tutoring',        'Python and Java, 1 hour session',        50.00, 'service'),
    (3, 2, 'Pens Pack (10 pieces)',       'Blue gel pens, unused',                  10.00, 'product'),
    (3, 3, 'Scientific Calculator',       'Casio fx-991, works perfectly',          60.00, 'product'),
    (3, 5, 'Poster and Slides Design',    'Design for presentations and projects',  80.00, 'service'),
    (2, 3, 'USB Flash Drive 64GB',        'Barely used',                            20.00, 'product');

-- Orders (buyer_id: 4 = Sara, 5 = Fahad)
INSERT INTO orders (buyer_id, listing_id, status) VALUES
    (4, 1, 'completed'),
    (4, 3, 'pending'),
    (5, 5, 'accepted');

-- Mark the sold listing
UPDATE listings SET status = 'sold' WHERE listing_id = 1;
 

