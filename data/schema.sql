-- ParallelShop BigQuery Schema

CREATE SCHEMA IF NOT EXISTS `parallelshop`;

-- Products catalog
CREATE TABLE IF NOT EXISTS `parallelshop.products` (
    product_id INT64,
    product_name STRING,
    aisle_id INT64,
    department_id INT64,
    price FLOAT64
);

-- Orders metadata
CREATE TABLE IF NOT EXISTS `parallelshop.orders` (
    order_id INT64,
    user_id INT64,
    eval_set STRING,
    order_number INT64,
    order_dow INT64,
    order_hour_of_day INT64,
    days_since_prior_order FLOAT64
);

-- Order line items
CREATE TABLE IF NOT EXISTS `parallelshop.order_products` (
    order_id INT64,
    product_id INT64,
    add_to_cart_order INT64,
    reordered INT64
);

-- Pruned sample orders for quick iteration (2000 active shoppers)
CREATE OR REPLACE TABLE `parallelshop.sample_orders` AS
SELECT * FROM `parallelshop.orders`
WHERE user_id IN (
    SELECT user_id 
    FROM `parallelshop.orders` 
    GROUP BY user_id 
    HAVING COUNT(*) >= 10 
    LIMIT 2000
);

-- Customer personas table
CREATE TABLE IF NOT EXISTS `parallelshop.customer_personas` (
    user_id INT64,
    price_sensitivity FLOAT64,
    brand_loyalty FLOAT64,
    avg_basket_size FLOAT64,
    persona STRING,
    top_products STRING  -- JSON array of top 20 product names & IDs
);
