
with funnel_stages as (
    select
        campaign_id,
        country,
        device_type,
        
        -- Step 1: View
        sum(case when action = 'view' then 1 else 0 end) as views,
        
        -- Step 2: Click
        sum(case when action = 'click' then 1 else 0 end) as clicks,
        
        -- Step 3: Purchase
        sum(case when action = 'purchase' then 1 else 0 end) as purchases

    from {{ ref('int_events') }}
    where not is_bot -- Filter out bots for clean funnel
    group by 1, 2, 3
)

select 
    *,
    -- Conversion Rates
    safe_divide(clicks, views) as click_ctr,
    safe_divide(purchases, clicks) as conversion_rate
from funnel_stages
order by purchases desc
