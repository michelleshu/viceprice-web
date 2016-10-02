select l.name, ah.*, dd.* from "vp_location" l
join "vp_location_deals" ld
on l."id" = ld."location_id"
join "vp_deal" d
on ld."deal_id" = d."id"
join "vp_deal_dealDetails" ddd
on ddd."deal_id" = d."id"
join "vp_dealdetail" dd
on dd."id" = ddd."dealdetail_id"
join "vp_deal_activeHours" dah
on dah."deal_id" = d.id
join "vp_activehour" ah
on dah."activehour_id" = ah.id
order by l.id, ah."dayofweek"