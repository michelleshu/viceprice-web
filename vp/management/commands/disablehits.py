from django.conf import settings
from django.core.management.base import BaseCommand
from boto.mturk import connection
from vp.models import MTurkLocationInfo, MTurkLocationInfoStat

class Command(BaseCommand):
    help = 'Disable all active HITs'
    args = '<site>'

    def handle(self, *args, **options):
        conn = connection.MTurkConnection(
            aws_access_key_id = settings.AWS_ACCESS_KEY,
            aws_secret_access_key = settings.AWS_SECRET_KEY,
            host = settings.MTURK_HOST)

        hits = list(conn.get_all_hits())

        for hit in hits:
            conn.disable_hit(hit.HITId)

        # Remove all MTurkLocationInfo and Stats
        for mturk_location_info in list(MTurkLocationInfo.objects.all()):
            if mturk_location_info.stat != None:
                mturk_location_info.stat.delete()
            mturk_location_info.delete()