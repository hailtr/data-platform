with source as (
    select * from {{ source('bridge', 'events') }}
),

renamed as (
    select
        -- IDs (Ensure they are strings)
        cast(event_id as string) as event_id,
        cast(session_id as string) as session_id,
        cast(user_id as string) as user_id,
        
        -- Event Details
        cast(action as string) as action,
        cast(value as float64) as value,
        
        -- Context (Extract from JSON/Struct if needed, or keeping flat)
        -- Standardize NULLs to 'XX' to match legacy placeholder pattern
        coalesce(cast(country as string), 'XX') as country,
        cast(device_type as string) as device_type,
        
        -- Timestamps
        -- Assuming 'timestamp' in Parquet is Unix epoch (int/float)
        timestamp_seconds(cast(timestamp as int64)) as event_at
        
    from source
)

select * from renamed
