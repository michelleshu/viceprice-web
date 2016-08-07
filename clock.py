from apscheduler.schedulers.blocking import BlockingScheduler
from rq import Queue
from worker import conn
from vp.management.commands import updatemturk, getfacebookdata
import pytz
import logging

sched = BlockingScheduler()
logging.basicConfig()
eastern_timezone = pytz.timezone('US/Eastern')
q = Queue(connection = conn)

@sched.scheduled_job('cron', minute='0-59/10', second='0', timezone=eastern_timezone)
def queue_mturk_update():
    print('MTurk update queued')
    q.enqueue(updatemturk.run)
    
@sched.scheduled_job('cron', hour='0', minute='0', second='0', timezone=eastern_timezone)
def queue_facebook_update():
    print('Facebook update queued')
    q.enqueue(getfacebookdata.run)
    
@sched.scheduled_job('cron', hour='1', minute='0', second='0', timezone=eastern_timezone)
def queue_fill_business_close_update():
    print('Fill Business Close update queued')
    q.enqueue(fillbusinessclosehours.run)

sched.start()