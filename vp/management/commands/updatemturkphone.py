__author__ = 'michelleshu'

from django.core.management.base import BaseCommand
from vp.mturk.mturk_update_phone_tasks import *
import updatedb

def run_phone_update():
    update_phone_tasks()
    updatedb.write_mturk_deals_to_db()

class Command(BaseCommand):
    help = 'Runs Mechanical Turk tasks for all website locations that require updates and writes completed info to db'
    args = '<site>'

    def handle(self, *args, **options):
        run_phone_update()