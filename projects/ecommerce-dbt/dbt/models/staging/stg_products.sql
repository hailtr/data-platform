-- Staging model for products
-- Cleans and standardizes product dimension data

with source_data as (
    select
        product_id,
        category,
        price,
        supplier,
        created_at,
        updated_at
    from {{ source('operational', 'products') }}
),

cleaned as (
    select
        product_id,
        lower(trim(category)) as category,
        price,
        trim(supplier) as supplier,
        created_at,
        updated_at
    from source_data
    where product_id is not null
      and price >= 0
)

select * from cleaned


