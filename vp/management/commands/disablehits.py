from django.core.management.base import BaseCommand
from boto.mturk import connection
from vp.mturk.mturk_utilities import *

class Command(BaseCommand):
    help = 'Runs Mechanical Turk tasks for all website locations that require updates and writes completed info to db'
    args = '<site>'

    def handle(self, *args, **options):
        conn = connection.MTurkConnection(aws_access_key_id=ACCESS_ID, aws_secret_access_key=SECRET_KEY, host=HOST)
        hits = list(conn.get_all_hits())
        for hit in hits:
            conn.disable_hit(hit.HITId)