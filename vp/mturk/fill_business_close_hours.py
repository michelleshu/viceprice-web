import django
from django.db import connection
from vp.models import ActiveHour

def update():
    
    django.setup()
    
    business_hours_query = "SELECT ahd.\"id\" AS activeHourId, ahl.\"start\" AS businessStart, ahl.\"end\" AS businessEnd \
        FROM \"vp_deal_activeHours\" dah \
        JOIN \"vp_activehour\" ahd \
        ON dah.\"activehour_id\" = ahd.\"id\" \
        JOIN \"vp_location_deals\" ld \
        ON ld.\"deal_id\" = dah.\"deal_id\" \
        JOIN \"vp_location_activeHours\" lah \
        ON lah.\"location_id\" = ld.\"location_id\" \
        JOIN \"vp_activehour\" ahl \
        ON lah.\"activehour_id\" = ahl.\"id\" AND ahl.\"dayofweek\" = ahd.\"dayofweek\" \
        WHERE ahd.\"end\" IS NULL \
        ORDER BY ahd.\"id\""
        
    cursor = connection.cursor()
    cursor.execute(business_hours_query)
    rows = cursor.fetchall()
    
    for row in rows:
        active_hour = ActiveHour.objects.get(id = int(row[0]))
        active_hour.end = row[2]
        active_hour.save()