-- Staging model for orders
-- Cleans and standardizes operational order data

with source_data as (
    select
        order_id,
        user_id,
        product_id,
        timestamp as order_timestamp,
        amount as order_amount,
        status as order_status,
        quantity as order_quantity,
        created_at,
        updated_at
    from {{ source('operational', 'orders') }}
),

cleaned as (
    select
        order_id,
        user_id,
        product_id,
        order_timestamp,
        order_amount,
        lower(trim(order_status)) as order_status,
        order_quantity,
        created_at,
        updated_at
    from source_data
    where order_id is not null
      and user_id is not null
      and product_id is not null
      and order_amount >= 0
      and order_quantity > 0
)

select * from cleaned


