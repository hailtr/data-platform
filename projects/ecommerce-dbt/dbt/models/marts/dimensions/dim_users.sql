-- User dimension table
-- Provides user attributes for analytics

select
    user_id,
    signup_date,
    country,
    tier,
    created_at,
    updated_at,
    current_timestamp as dbt_updated_at
from {{ ref('stg_users') }}


