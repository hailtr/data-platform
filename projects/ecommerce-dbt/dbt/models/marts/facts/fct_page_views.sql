-- Page views fact table
-- Provides page view-level facts for analytics

select
    pv.view_id,
    pv.user_id,
    pv.product_id,
    pv.view_timestamp,
    date_trunc('day', pv.view_timestamp)::date as view_date,
    pv.session_id,
    pv.page_url,
    pv.duration_seconds,
    pv.created_at,
    current_timestamp as dbt_updated_at
from {{ ref('stg_page_views') }} pv


