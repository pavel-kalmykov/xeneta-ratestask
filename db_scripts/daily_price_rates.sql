with
    -- 1. We start with two **recursive** CTEs to find all regions relevant to our
    -- query, including sub-regions of the origin and destination.
    -- UPDATE: We don't do that anymore because we turned that recursive CTE into
    -- a materialized view (because regions hardly change)
    --
    -- 2. We then use two CTEs to find all relevant origin and destination ports,
    -- unionising ports in the specified regions (and their recursive sub-regions).
    origin_ports as (
        -- Use the port code if it's a port code indeed.
        select code
        from ports
        where code = :origin
        union
        -- Include all the ports in the origin region recursively (this is where
        -- the magic happens).
        select code
        from ports p
        join mv_region_hierarchy rh on p.parent_slug = rh.slug
        where rh.slug = :origin or rh.parent_slug = :origin
    ),
    destination_ports as (
        select code
        from ports
        where code = :destination
        union
        select code
        from ports p
        join mv_region_hierarchy rh on p.parent_slug = rh.slug
        where rh.slug = :destination or rh.parent_slug = :destination
    ),
    -- 3. Now we calculate the average prices for origin and destination
    -- ports, filtering by date and ensuring we have at least n rows per day.
    avg_prices as (
        select day, round(avg(price), 0) as average_price
        from prices
        where
            orig_code in (select code from origin_ports)
            and dest_code in (select code from destination_ports)
            and day between :date_from and :date_to
        group by day
        having count(price) >= :min_prices_per_day
    ),
    -- 4. We also generate all dates in the requested range. This way, we
    -- have a row for each day (even if it does not appear in price_data).
    dates as (
        select
            generate_series(
                -- There needs to be a space between the variable and the cast for
                -- SQLAlchemy not to get confused.
                :date_from ::date,
                :date_to ::date,
                '1 day' ::interval
            )::date as day
    )
-- 5. Finally, we left join the generated dates with the price data.
select d.day, ap.average_price
from dates d
left join avg_prices ap on d.day = ap.day
order by d.day
;
