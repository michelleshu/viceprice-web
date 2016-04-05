-- Show aggregate category count
select lc."id", lc."name", lc."isBaseCategory", lc."parentCategory_id", count(*) as "count"
from "vp_location" l
join "vp_location_locationCategories" llc
on l."id" = llc."location_id"
join "vp_locationcategory" lc
on llc."locationcategory_id" = lc."id"
where "isBaseCategory" = true
group by lc."id", lc."name", lc."isBaseCategory", lc."parentCategory_id"
order by "count" desc

select * from "

select lc."name", count(*) as "count"
from "vp_location" l
join "vp_location_locationCategories" llc
on l."id" = llc."location_id"
join "vp_locationcategory" lc
on llc."locationcategory_id" = lc."id"
where lc."parentCategory_id" = 30
group by lc."name"
order by "count" desc

-- Restaurant Subcategories to Delete
Bar
Restaurant
Bar & Grill
Caterer
Event Venue
Deli
Nightlife
Food & Grocery
Deck & Patio
Butcher
Miniature Golf
Art Gallery
Performance Venue
Live & Raw Food Restaurant
Bands & Musicians
Night Club
Shopping & Retail
Neighborhood
Historical Place
Late Night Restaurant

-- Bar Subcategories to Delete
Bar
Restaurant
Late Night Restaurant
Sports & Recreation
DJ
Italian Restaurant
Mexican Restaurant
Barbecue Restaurant
Social Club
Latin American Restaurant
Bands & Musicians


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