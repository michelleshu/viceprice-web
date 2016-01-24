from django.conf import settings
from django.core.management.base import BaseCommand
from boto.mturk import connection

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