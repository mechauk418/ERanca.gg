from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django_apscheduler.jobstores import register_events
from .views import gainrp, resetrp, rpeff


def start():
    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    register_events(scheduler)

    scheduler.add_job(
        resetrp,
        trigger=CronTrigger(day_of_week="tue", hour="22", minute="45"),
        max_instances=1,
        name="resetrp",
    )

    scheduler.add_job(
        gainrp(0,333),
        trigger=CronTrigger(day_of_week="tue", hour="22", minute="50"),
        max_instances=1,
        name="gainrp",
    )
    scheduler.add_job(
        gainrp(333,666),
        trigger=CronTrigger(day_of_week="tue", hour="23", minute="10"),
        max_instances=1,
        name="gainrp2",
    )
    scheduler.add_job(
        gainrp(666,1000),
        trigger=CronTrigger(day_of_week="tue", hour="23", minute="30"),
        max_instances=1,
        name="gainrp3",
    )
    scheduler.add_job(
        rpeff,
        trigger=CronTrigger(day_of_week="tue", hour="23", minute="50"),
        max_instances=1,
        name="rpeff",
    )

    scheduler.start()

#test