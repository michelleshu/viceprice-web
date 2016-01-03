select d.description, dow.day, tf."startTime", tf."endTime", l.name
from "vp_deal" d
join "vp_dayofweek" dow
on d."dealHour_id" = dow."businessHour_id"
join "vp_timeframe" tf
on d."dealHour_id" = tf."businessHour_id"
join "vp_location_deals" ld
on d.id = ld."deal_id"
join "vp_location" l
on l.id = ld."location_id"