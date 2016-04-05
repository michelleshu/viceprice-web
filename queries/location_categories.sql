-- Show aggregate category count
select l."id", l."name"
from "vp_location" l
join "vp_location_locationCategories" llc
on l."id" = llc."location_id"
join "vp_locationcategory" lc
on llc."locationcategory_id" = lc."id"
where "parentCategory_id" in (26, 136, 132, 183, 112, 217, 156, 204, 159)
group by lc."id", lc."name", lc."isBaseCategory", lc."parentCategory_id"
order by "count" desc

select * from "vp_locationcategory"
where id in (30, 155, 63)

select lc."id", lc."name", count(*) as "count"
from "vp_location" l
join "vp_location_locationCategories" llc
on l."id" = llc."location_id"
join "vp_locationcategory" lc
on llc."locationcategory_id" = lc."id"
group by lc."id", lc."name"
order by "count" desc


-- Count number of subcategories
select c."count", count(*) as "countMultiplicity"
from
(select l."id", count(*) as "count"
from "vp_location" l
join "vp_location_locationCategories" llc
on l."id" = llc."location_id"
join "vp_locationcategory" lc
on llc."locationcategory_id" = lc."id"
where lc."isBaseCategory" = false
group by l."id"
order by "count" desc) c
group by c."count"

select * from "vp_location" l
left join "vp_location_locationCategories" llc
on l."id" = llc."location_id"
where llc."id" is null
