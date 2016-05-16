select ah.* from "vp_location_deals" ld
join "vp_deal_activeHours" dah
on ld."deal_id" = dah."deal_id"
join "vp_activehour" ah
on dah."activehour_id" = ah."id"
where ld."location_id" = 2805

update "vp_activehour" ah
set "end" = '19:00'
where ah."id" IN (3773, 3772, 3771, 3770, 3769, 3768, 3767)
