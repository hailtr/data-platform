-- Product dimension table
-- Provides product attributes for analytics

select
    product_id,
    category,
    price,
    supplier,
    created_at,
    updated_at,
    current_timestamp as dbt_updated_at
from {{ ref('stg_products') }}


