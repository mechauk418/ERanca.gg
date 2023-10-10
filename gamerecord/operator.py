from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django_apscheduler.jobstores import register_events
from .views import gainrp


def start():
    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    register_events(scheduler)

    scheduler.add_job(
        gainrp,
        trigger=CronTrigger(day_of_week="tue", hour="12", minute="13"),
        max_instances=1,
        name="gainrp",
    )

    scheduler.start()