from django.core.management.base import BaseCommand
from vp.models import Location

class Command(BaseCommand):
    help = 'Format websites to begin with http://www.'
    args = '<site>'

    def handle(self, *args, **options):
        locations = Location.objects.all()

        for location in locations:
            if location.website == "":
                location.website = None
                location.save()

            if location.website != None:
                website = location.website.strip("\"' ")

                if not website.startswith("http://") and not website.startswith("https://"):
                    website = "http://" + website

                if website.find("www") == -1:
                    index = website.find("://") + 3
                    website = website[:index] + "www." + website[index:]

                location.website = website
                location.save()