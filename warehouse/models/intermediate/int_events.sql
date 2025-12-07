
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
        -- Since there are only 2 countries for users, (XX and BR/FR/CA), we can use MAX and filter XX.
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
        e.device_type,
        e.event_at,
        -- Pass Campaign ID
        e.campaign_id,
        
        -- Pass Original Value (For Audit)
        e.value as original_value,
        
        -- The Fix: Use known country if available, otherwise keep what we have (XX)
        coalesce(map.known_country, e.country) as country,
        
        -- Logic: Regional Pricing (PPP Adjustment)
        -- US/UK/DE/JP = 1.0 (Full Value)
        -- BR/FR/CA = 0.5 (Tier 2)
        -- XX/Others = 0.2 (Tier 3)
        case 
            when coalesce(map.known_country, e.country) in ('US', 'UK', 'DE', 'JP') then e.value
            when coalesce(map.known_country, e.country) in ('BR', 'FR', 'CA') then e.value * 0.5
            else e.value * 0.2
        end as adjusted_value,
        
        -- Logic: Sales Flag
        case when e.action = 'purchase' then true else false end as is_sale,
        
        -- Logic: Bot Detection (Phase 3)
        -- Identify High-Frequency Sessions
        count(*) over (partition by e.session_id) as session_event_count,
        case when count(*) over (partition by e.session_id) > 50 then true else false end as is_bot
        
        
    from events e
    left join user_country_mapping map on e.user_id = map.user_id
)

select * from enriched
