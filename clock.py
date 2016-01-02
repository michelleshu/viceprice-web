from apscheduler.schedulers.blocking import BlockingScheduler
from rq import Queue
from worker import conn
from vp.management.commands import updatemturkweb, updatemturkphone
import pytz
import logging

# sched = BlockingScheduler()
# logging.basicConfig()
# eastern_timezone = pytz.timezone('US/Eastern')
# q = Queue(connection = conn)
#
# @sched.scheduled_job('cron', minute='5-55/10', second='0', timezone=eastern_timezone)
# def queue_mturk_website_update():
#     print('MTurk website update queued')
#     q.enqueue(updatemturkweb.run_website_update)
#
# @sched.scheduled_job('cron', hour='11-19', minute='*/30', second='0', timezone=eastern_timezone)
# def queue_mturk_phone_update():
#     print('MTurk phone update queued')
#     q.enqueue(updatemturkphone.run_phone_update)
#
# sched.start()