-- Staging model for inventory changes
-- Cleans and standardizes inventory change data

with source_data as (
    select
        id as inventory_change_id,
        product_id,
        timestamp as change_timestamp,
        stock_change,
        current_stock,
        warehouse_id,
        created_at
    from {{ source('operational', 'inventory_changes') }}
),

cleaned as (
    select
        inventory_change_id,
        product_id,
        change_timestamp,
        stock_change,
        current_stock,
        warehouse_id,
        created_at
    from source_data
    where product_id is not null
      and current_stock >= 0
)

select * from cleaned


