from django.core.management.base import BaseCommand
from vp.mturk import mturk_update_phone_tasks
import updatedb


class Command(BaseCommand):
    help = 'Runs Mechanical Turk tasks for all website locations that require updates and writes completed info to db'
    args = '<site>'

    def handle(self, *args, **options):
        mturk_update_phone_tasks.update()
        updatedb.write_mturk_deals_to_db()