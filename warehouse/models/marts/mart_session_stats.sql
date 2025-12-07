
with session_metrics as (
    select
        session_id,
        user_id,
        country,
        is_bot,
        
        -- Session Time
        min(event_at) as session_start,
        max(event_at) as session_end,
        timestamp_diff(max(event_at), min(event_at), SECOND) as duration_seconds,
        
        -- Engagement
        count(*) as total_events,
        count(distinct action) as unique_actions,
        sum(adjusted_value) as session_revenue

    from {{ ref('int_events') }}
    group by 1, 2, 3, 4
)

select 
    *,
    case when total_events = 1 then true else false end as is_bounce
from session_metrics
