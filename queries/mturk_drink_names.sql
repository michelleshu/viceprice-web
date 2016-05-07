select ah.*, dd.*, m.* from "vp_deal" d
join "vp_deal_activeHours" dah
on dah."deal_id" = d."id"
join "vp_activehour" ah
on ah."id" = dah."activehour_id"
join "vp_deal_dealDetails" ddd
on ddd."deal_id" = d."id"
join "vp_dealdetail" dd
on dd."id" = ddd."dealdetail_id"
join "vp_dealdetail_mturkDrinkNameOptions" ddm
on ddm."dealdetail_id" = dd."id"
join "vp_mturkdrinknameoption" m
on ddm."mturkdrinknameoption_id" = m."id"
where d."confirmed" = 'f'
order by dd."id", m."name", ah."dayofweek"
