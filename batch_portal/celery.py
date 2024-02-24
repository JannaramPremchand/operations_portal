
from celery import Celery
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'batch_portal.settings')
import django
django.setup()
from celery import Celery



from portal.models import  mycelerytask
# set the default Django settings module for the 'celery' program.


app = Celery('batch_portal')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')
from celery import Celery
app.conf.enable_utc = False

app.conf.update(timezone = 'Asia/Kolkata')

# Load task modules from all registered Django app configs.
from django.apps import apps
app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

x = mycelerytask.objects.all().values().order_by('-mytaskId')[0]['access_token'].replace("\n",'')
from celery.schedules import crontab
import json

# from portal import task
# from portal.task import add_api_data

app.conf.beat_schedule = {
    'add-every-day at every 2 minute 30seconds': {
        'task': 'portal.task.add_api_data',
        'schedule': 150.0,
        'kwargs':{"fun":json.dumps(x)[:][0:][1:-1]}
    },
}

# app.conf.beat_schedule = {
#     'add-every-day at every 2 minute 30seconds': {
#         'task': 'portal.task.add_meeting_attendence',
#         'schedule': 150.0,
#         'kwargs':{"fun":json.dumps(x)[:][0:][1:-1]}
#     },
# }

# app.conf.beat_schedule = {
#     'add-every-day at every 01:30 a.m.': {
#         'task': 'portal.task.add_meeting_attendence',
#         'schedule': crontab(hour=01, minute=30),
#         'kwargs':{"fun":json.dumps(x)[:][0:][1:-1]}
#     },
# }