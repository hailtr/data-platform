-- Time dimension table
-- Provides time attributes for analytics

with date_spine as (
    select
        date_day,
        date_day as date_id,
        extract(year from date_day) as year,
        extract(quarter from date_day) as quarter,
        extract(month from date_day) as month,
        extract(week from date_day) as week,
        extract(day from date_day) as day,
        extract(dow from date_day) as day_of_week,
        extract(doy from date_day) as day_of_year,
        to_char(date_day, 'Month') as month_name,
        to_char(date_day, 'Day') as day_name,
        case when extract(dow from date_day) in (0, 6) then true else false end as is_weekend
    from (
        select generate_series(
            date_trunc('year', current_date - interval '2 years'),
            current_date + interval '1 year',
            interval '1 day'
        )::date as date_day
    ) dates
)

select * from date_spine


