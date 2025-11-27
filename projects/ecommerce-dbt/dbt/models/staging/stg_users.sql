-- Staging model for users
-- Cleans and standardizes user dimension data

with source_data as (
    select
        user_id,
        signup_date,
        country,
        tier,
        created_at,
        updated_at
    from {{ source('operational', 'users') }}
),

cleaned as (
    select
        user_id,
        signup_date,
        upper(trim(country)) as country,
        lower(trim(tier)) as tier,
        created_at,
        updated_at
    from source_data
    where user_id is not null
)

select * from cleaned


