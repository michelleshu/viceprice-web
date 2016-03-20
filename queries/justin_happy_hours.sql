SELECT l."name" AS "Location",
	j."day" AS "Day", j."datasource" AS "Justin Data Source", l."dealDataSource" AS "MTurk Data Source",
	j."starttime" AS "Justin Start Time", j."endtime" AS "Justin End Time", tf."startTime" AS "MTurk Start Time", tf."endTime" AS "MTurk End Time", 
	j."dealdescription" AS "Justin Description", d."description" AS "MTurk Description"
FROM "justin_locationinfo" j
LEFT JOIN "vp_location" l
ON j."location_id" = l.id
LEFT JOIN "vp_location_deals" ld
ON l.id = ld."location_id"
LEFT JOIN "vp_deal" d
ON ld."deal_id" = d.id
LEFT JOIN "vp_dayofweek" dow
ON d."dealHour_id" = dow."businessHour_id"
LEFT JOIN "vp_timeframe" tf
ON d."dealHour_id" = tf."businessHour_id"
WHERE j."day" = dow."day"
