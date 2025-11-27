-- Orders fact table
-- Provides order-level facts for analytics

select
    o.order_id,
    o.user_id,
    o.product_id,
    o.order_timestamp,
    date_trunc('day', o.order_timestamp)::date as order_date,
    o.order_amount,
    o.order_status,
    o.order_quantity,
    o.order_amount * o.order_quantity as total_amount,
    o.created_at,
    o.updated_at,
    current_timestamp as dbt_updated_at
from {{ ref('stg_orders') }} o


