
from celery import Celery
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'batch_portal.settings')
import django
django.setup()
from celery import Celery



from portal.models import  mycelerytask
# set the default Django settings module for the 'celery' program.


app = Celery('batch_portal')
app.conf.enable_utc = True

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')
from celery import Celery


# Load task modules from all registered Django app configs.
from django.apps import apps
app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

#x = mycelerytask.objects.all().values().order_by('-mytaskId')[0]['access_token'].replace("\n",'')
from celery.schedules import crontab
import json

from portal import task


# app.conf.beat_schedule = {
#     'add-every-day at every night 10.30': {
#         'task': 'portal.task.add_meeting_attendence',
#         'schedule': crontab(minute=30, hour=22),
#         'kwargs':{}
#     },
# }

# app.conf.beat_schedule = {
#     'add-every-day at every 01:30 a.m.': {
#         'task': 'portal.task.add_meeting_attendence',
#         'schedule': crontab(hour=01, minute=30),
#         'kwargs':{"fun":json.dumps(x)[:][0:][1:-1]}
#     },
# }




app.conf.beat_schedule = {
    'add-every-day at every 15:30 pm': {
        'task': 'portal.task.add_api_data',
        'schedule': crontab(minute=30, hour=15),
        'kwargs':{}
    },
}

app.conf.beat_schedule = {
    'add-every-day at every 16:8 pm': {
        'task': 'portal.task.hubspot_delete_dbdata',
        'schedule': crontab(minute=8, hour=16),
        'kwargs':{}
    },
}


app.conf.beat_schedule = {
    'add-every-day at every 16:19 pm': {
        'task': 'portal.task.hub_spot_task',
        'schedule': crontab(minute=19, hour=16),
        'kwargs':{}
    },
}


app.conf.beat_schedule = {
    'add-every-day at every 16:40 pm': {
        'task': 'portal.task.hub_spot_task_2',
        'schedule': crontab(minute=40, hour=16),
        'kwargs':{}
    },
}

app.conf.beat_schedule = {
    'add-every-day at every 17:11 pm': {
        'task': 'portal.task.hubspot_update_data',
        'schedule': crontab(minute=11, hour=17),
        'kwargs':{}
    },
}


