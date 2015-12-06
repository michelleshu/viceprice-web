from apscheduler.schedulers.blocking import BlockingScheduler
from rq import Queue
from worker import conn
from vp.management.commands.updatemturkdata import printUpdate
import pytz

sched = BlockingScheduler()
eastern_timezone = pytz.timezone('US/Eastern')
q = Queue(connection = conn)

@sched.scheduled_job('cron', minute='5-55/10', second='0', timezone=eastern_timezone)
def queue_mturk_website_update():
    print('MTurk website update queued')
    result = q.enqueue(printUpdate, True);
    print(result)

@sched.scheduled_job('cron', minute='*/30', second='0', timezone=eastern_timezone)
def queue_mturk_phone_update():
    print('MTurk phone update queued')
    result = q.enqueue(printUpdate, False);
    print(result)

sched.start()