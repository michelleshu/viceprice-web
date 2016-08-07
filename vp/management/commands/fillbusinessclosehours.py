from django.core.management.base import BaseCommand
from vp.mturk import fill_business_close_hours

class Command(BaseCommand):
    args = '<site>'
    
    def handle(self, *args, **options):
        fill_business_close_hours.update()
        
def run():
    fill_business_close_hours.update()