
{{ config(
    materialized='table'
) }}

with events as (
    select * from {{ ref('int_events') }}
),

metrics as (
    select
        country,
        device_type,
        
        -- Metrics
        count(distinct session_id) as total_sessions,
        count(distinct user_id) as total_users,
        count(*) as total_events,
        
        sum(case when action = 'purchase' then value else 0 end) as total_revenue,
        sum(case when action = 'click' then 1 else 0 end) as total_clicks,
        sum(case when action = 'view' then 1 else 0 end) as total_views
        
    from events
    group by 1, 2
)

select * from metrics
order by total_revenue desc
