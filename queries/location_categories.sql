-- Show aggregate category count
select lc."id", lc."name", lc."isBaseCategory", lc."parentCategory_id", count(*) as "count"
from "vp_location" l
join "vp_location_locationCategories" llc
on l."id" = llc."location_id"
join "vp_locationcategory" lc
on llc."locationcategory_id" = lc."id"
group by lc."id", lc."name", lc."isBaseCategory", lc."parentCategory_id"
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