
{{ config(
    materialized='table'
) }}

with events as (
    select * from {{ ref('stg_events') }}
),

user_country_mapping as (
    select
        user_id,
        -- Find the "Real" country for a user (ignoring 'XX' and NULLs)
        -- We pick MAX just to pick ONE if they have multiple (e.g. moved from UK to FR). 
        -- In a real app we might use "Most Frequent" or "Latest", but MAX is sufficient here.
        max(case when country != 'XX' then country end) as known_country
    from events
    group by 1
),

enriched as (
    select
        e.event_id,
        e.session_id,
        e.user_id,
        e.action,
        e.value,
        e.device_type,
        e.event_at,
        
        -- The Fix: Use known country if available, otherwise keep what we have (XX)
        coalesce(map.known_country, e.country) as country
        
    from events e
    left join user_country_mapping map on e.user_id = map.user_id
)

select * from enriched
