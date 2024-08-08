-- This query shares
with recursive
    origin_region_hierarchy as (
        select slug
        from regions
        where slug = :origin
        union all
        select r.slug
        from regions r
        join origin_region_hierarchy rh on r.parent_slug = rh.slug
    ),
    destination_region_hierarchy as (
        select slug
        from regions
        where slug = :destination
        union all
        select r.slug
        from regions r
        join destination_region_hierarchy rh on r.parent_slug = rh.slug
    ),
    origin_ports as (
        select code
        from ports
        where code = :origin
        union
        select code
        from ports
        join origin_region_hierarchy rh on parent_slug = rh.slug
    ),
    destination_ports as (
        select code
        from ports
        where code = :destination
        union
        select code
        from ports
        join destination_region_hierarchy rh on parent_slug = rh.slug
    )
select
    (select count(*) from origin_ports) as origin_matches,
    (select count(*) from destination_ports) as destination_matches
;
