from django.core.management.base import BaseCommand
from vp.mturk import update_mturk_tasks


class Command(BaseCommand):
    help = 'Runs Mechanical Turk tasks for all website locations that require updates and writes completed info to db'
    args = '<site>'

    def handle(self, *args, **options):
        update_mturk_tasks.update()

def run():
    update_mturk_tasks.update()