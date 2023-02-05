import os
from celery import Celery

# commands:
# celery -A conf worker -l info
# celery -A conf beat -l info -S django

# ensure that settings is available through the DJANGO_SETTINGS_MODULE key
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")
app = Celery("conf")

# set django settings file as the configuration file as the configuration file for celery
app.config_from_object("django.conf:settings", namespace="CELERY")
# tell celery to automatically find all tasks in our django project
app.autodiscover_tasks()
