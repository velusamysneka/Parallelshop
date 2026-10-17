-- ParallelShop Customer Segmentation & Persona Generation
-- Computes behavioral metrics per customer and categorizes into personas:
-- 1. bargain_hunter: price sensitivity > 0.60
-- 2. brand_loyal: brand loyalty (reorder rate) > 0.60
-- 3. bulk_shopper: avg basket size > 15 items
-- 4. convenience_shopper: baseline / balanced shopper

CREATE OR REPLACE TABLE `parallelshop.customer_personas` AS
WITH product_prices AS (
    SELECT 
        p.product_id,
        p.aisle_id,
        p.price,
        MIN(p.price) OVER(PARTITION BY p.aisle_id) AS min_aisle_price
    FROM `parallelshop.products` p
),
user_order_stats AS (
    SELECT 
        o.user_id,
        op.order_id,
        op.product_id,
        op.reordered,
        pp.price,
        CASE WHEN pp.price <= pp.min_aisle_price * 1.05 THEN 1 ELSE 0 END AS is_cheapest
    FROM `parallelshop.sample_orders` o
    JOIN `parallelshop.order_products` op ON o.order_id = op.order_id
    JOIN product_prices pp ON op.product_id = pp.product_id
),
user_metrics AS (
    SELECT 
        user_id,
        COUNT(DISTINCT order_id) AS total_orders,
        COUNT(product_id) AS total_items,
        SAFE_DIVIDE(COUNT(product_id), COUNT(DISTINCT order_id)) AS avg_basket_size,
        SAFE_DIVIDE(SUM(reordered), COUNT(product_id)) AS brand_loyalty,
        SAFE_DIVIDE(SUM(is_cheapest), COUNT(product_id)) AS price_sensitivity
    FROM user_order_stats
    GROUP BY user_id
),
user_top_products AS (
    SELECT 
        user_id,
        TO_JSON_STRING(
            ARRAY_AGG(
                STRUCT(product_id, product_name, purchase_count) 
                ORDER BY purchase_count DESC 
                LIMIT 20
            )
        ) AS top_products
    FROM (
        SELECT 
            o.user_id,
            p.product_id,
            p.product_name,
            COUNT(*) AS purchase_count
        FROM `parallelshop.sample_orders` o
        JOIN `parallelshop.order_products` op ON o.order_id = op.order_id
        JOIN `parallelshop.products` p ON op.product_id = p.product_id
        GROUP BY o.user_id, p.product_id, p.product_name
    )
    GROUP BY user_id
)
SELECT 
    m.user_id,
    ROUND(m.price_sensitivity, 4) AS price_sensitivity,
    ROUND(m.brand_loyalty, 4) AS brand_loyalty,
    ROUND(m.avg_basket_size, 2) AS avg_basket_size,
    CASE 
        WHEN m.price_sensitivity > 0.60 THEN 'bargain_hunter'
        WHEN m.brand_loyalty > 0.60 THEN 'brand_loyal'
        WHEN m.avg_basket_size > 15.0 THEN 'bulk_shopper'
        ELSE 'convenience_shopper'
    END AS persona,
    tp.top_products
FROM user_metrics m
JOIN user_top_products tp ON m.user_id = tp.user_id;
