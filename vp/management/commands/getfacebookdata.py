from django.core.management.base import BaseCommand
from vp.facebook import update_facebook_data

class Command(BaseCommand):
    args = '<site>'

    def handle(self, *args, **options):
        update_facebook_data.update()
        
def run():
    update_facebook_data.update()