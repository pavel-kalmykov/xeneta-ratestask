-- This query shares the first part of daily_price_rates.sql.
-- Check that file for more info
with
    origin_ports as (
        select code
        from ports
        where code = :origin
        union
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
    )
select
    (select count(*) from origin_ports) as origin_matches,
    (select count(*) from destination_ports) as destination_matches
;
