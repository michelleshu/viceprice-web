from apscheduler.schedulers.blocking import BlockingScheduler
import pytz

sched = BlockingScheduler()
eastern_timezone = pytz.timezone('US/Eastern')

@sched.scheduled_job('cron', minute='5-55/10', second='0', timezone=eastern_timezone)
def queue_mturk_website_update():
    print('MTurk website update queued')

@sched.scheduled_job('cron', minute='*/30', second='0', timezone=eastern_timezone)
def queue_mturk_phone_update():
    print('MTurk phone update queued')

sched.start()