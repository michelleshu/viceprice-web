select id, name, "happyHourWebsite" from "vp_location"
where name like '%Club%'
order by "id" desc

update "vp_location" 
set "happyHourWebsite" = ''
where id = 