-- Staging model for page views
-- Cleans and standardizes page view event data

with source_data as (
    select
        view_id,
        user_id,
        product_id,
        timestamp as view_timestamp,
        session_id,
        page_url,
        duration_seconds,
        created_at
    from {{ source('operational', 'page_views') }}
),

cleaned as (
    select
        view_id,
        user_id,
        product_id,
        view_timestamp,
        session_id,
        page_url,
        coalesce(duration_seconds, 0) as duration_seconds,
        created_at
    from source_data
    where view_id is not null
      and user_id is not null
      and session_id is not null
      and page_url is not null
)

select * from cleaned


