-- Daily sales aggregation
-- Provides daily sales metrics

select
    date_trunc('day', order_timestamp)::date as sale_date,
    count(distinct order_id) as total_orders,
    count(distinct user_id) as unique_customers,
    count(distinct product_id) as unique_products,
    sum(order_quantity) as total_quantity_sold,
    sum(order_amount * order_quantity) as total_revenue,
    avg(order_amount * order_quantity) as avg_order_value,
    sum(case when order_status = 'confirmed' then order_amount * order_quantity else 0 end) as confirmed_revenue,
    sum(case when order_status = 'cancelled' then order_amount * order_quantity else 0 end) as cancelled_revenue
from {{ ref('fct_orders') }}
group by 1
order by 1 desc


