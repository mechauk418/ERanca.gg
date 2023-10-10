from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django_apscheduler.jobstores import register_events
from .views import gainrp, gainrp2, gainrp3


def start():
    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    register_events(scheduler)

    scheduler.add_job(
        gainrp,
        trigger=CronTrigger(day_of_week="tue", hour="14", minute="00"),
        max_instances=1,
        name="gainrp",
    )
    scheduler.add_job(
        gainrp2,
        trigger=CronTrigger(day_of_week="tue", hour="14", minute="30"),
        max_instances=1,
        name="gainrp2",
    )
    scheduler.add_job(
        gainrp3,
        trigger=CronTrigger(day_of_week="tue", hour="15", minute="00"),
        max_instances=1,
        name="gainrp3",
    )

    scheduler.start()