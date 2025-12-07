
with source as (
    select * from {{ source('bridge', 'events') }}
),

renamed as (
    select
        -- IDs
        cast(event_id as string) as event_id,
        cast(session_id as string) as session_id,
        cast(user_id as string) as user_id,
        
        -- Dimensions
        -- Fix Missing Country (NULL -> 'XX')
        coalesce(cast(country as string), 'XX') as country,
        cast(device_type as string) as device_type,
        cast(action as string) as action,
        
        -- New Campaign Extraction (Phase 2)
        -- Accessing STRUCT field
        cast(context.campaign_id as string) as campaign_id,
        
        -- Metrics
        cast(value as float64) as value,
        
        -- Timestamps
        timestamp_seconds(cast(timestamp as int64)) as event_at

    from source
)

select * from renamed
