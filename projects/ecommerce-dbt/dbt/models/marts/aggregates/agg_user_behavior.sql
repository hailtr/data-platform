-- User behavior aggregation
-- Provides user-level behavior metrics

with user_orders as (
    select
        user_id,
        count(distinct order_id) as total_orders,
        sum(order_amount * order_quantity) as total_spent,
        avg(order_amount * order_quantity) as avg_order_value,
        min(order_timestamp) as first_order_date,
        max(order_timestamp) as last_order_date,
        count(distinct case when order_status = 'confirmed' then order_id end) as confirmed_orders,
        count(distinct case when order_status = 'cancelled' then order_id end) as cancelled_orders
    from {{ ref('fct_orders') }}
    group by 1
),

user_page_views as (
    select
        user_id,
        count(distinct view_id) as total_page_views,
        count(distinct session_id) as total_sessions,
        sum(duration_seconds) as total_time_on_site,
        avg(duration_seconds) as avg_session_duration,
        count(distinct product_id) as products_viewed
    from {{ ref('fct_page_views') }}
    group by 1
)

select
    coalesce(o.user_id, pv.user_id) as user_id,
    coalesce(o.total_orders, 0) as total_orders,
    coalesce(o.total_spent, 0) as total_spent,
    o.avg_order_value,
    o.first_order_date,
    o.last_order_date,
    o.confirmed_orders,
    o.cancelled_orders,
    coalesce(pv.total_page_views, 0) as total_page_views,
    coalesce(pv.total_sessions, 0) as total_sessions,
    coalesce(pv.total_time_on_site, 0) as total_time_on_site,
    pv.avg_session_duration,
    coalesce(pv.products_viewed, 0) as products_viewed,
    case 
        when o.total_orders > 0 and pv.total_page_views > 0 
        then o.total_orders::numeric / pv.total_page_views::numeric 
        else 0 
    end as conversion_rate
from user_orders o
full outer join user_page_views pv on o.user_id = pv.user_id


