from django.core.management.base import BaseCommand
from viceprice import settings
from vp.models import Location, ActiveHour
import csv
import datetime
import django

DAY_OF_WEEK = {
    "Monday": 1,
    "Tuesday": 2,
    "Wednesday": 3,
    "Thursday": 4,
    "Friday": 5,
    "Saturday": 6,
    "Sunday": 7
}

class Command(BaseCommand):
    args = '<site>'

    def handle(self, *args, **options):
        
        django.setup()
        
        with open(settings.BASE_DIR + '/vp/management/commands/BusinessHoursTilClose.csv', 'r') as file:
            business_name = None
            business_location = None
            start_day = None
            end_day = None
            start_time = None
            end_time = None

            reader = csv.reader(file)
            for row in reader:
                if row[0] != None and row[0] != '':
                    # Save last business's business hour info if it exists
                    if business_location != None:
                        business_location.save()

                    business_id = row[0]
                    try:
                        business_location = Location.objects.get(id=business_id)
                        print(business_location.name)
                    except Exception:
                        print("Skip")
                        continue

                    if (business_location != None):
                        business_hours = business_location.activeHours.all()
                        # Delete all old business hours info
                        for business_hour in business_hours:
                            business_hour.delete()

                if row[1] != None and row[1] != '':
                    start_day = DAY_OF_WEEK[row[1].replace(' ', '')]

                    if row[2] != None and row[2] != '':
                        end_day = DAY_OF_WEEK[row[2].replace(' ', '')]
                    else:
                        end_day = start_day

                    if row[3] != None and row[3] != '':
                        start_string = row[3]
                        if len(start_string) == 4:
                            start_string = "0" + start_string
                        start_time = datetime.datetime.strptime(start_string, '%H:%M').time()
                    else:
                        continue

                    if row[4] != None and row[4] != '':
                        end_string = row[4]
                        if len(end_string) == 4:
                            end_string = "0" + end_string
                        end_time = datetime.datetime.strptime(end_string, '%H:%M').time()
                    else:
                        continue

                    if business_location != None:
                        
                        day_of_week = start_day
                        
                        while (day_of_week <= end_day):
                            new_business_hour = ActiveHour(dayofweek = day_of_week, start = start_time, end = end_time)
                            new_business_hour.save()
                            business_location.activeHours.add(new_business_hour)
                            day_of_week += 1
                            
                        business_location.save()



