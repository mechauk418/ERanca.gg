from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django_apscheduler.jobstores import register_events, DjangoJobStore
from .views import gainrp, resetrp, rpeff


def start():

    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(),'default')
    register_events(scheduler)

    scheduler.add_job(
        resetrp,
        trigger=CronTrigger(day_of_week="wed", hour="11", minute="05"),
        id="resetrp",
        max_instances=1,
        replace_existing=True
    )
    scheduler.add_job(
        gainrp(0,333),
        trigger=CronTrigger(day_of_week="wed", hour="11", minute="10"),
        id="gainrp1",
        max_instances=1,
        replace_existing=True
    )
    scheduler.add_job(
        gainrp(333,666),
        trigger=CronTrigger(day_of_week="wed", hour="11", minute="30"),
        id="gainrp2",
        max_instances=1,
        replace_existing=True
    )
    scheduler.add_job(
        gainrp(666,1000),
        trigger=CronTrigger(day_of_week="wed", hour="11", minute="50"),
        id="gainrp3",
        max_instances=1,
        replace_existing=True
    )
    scheduler.add_job(
        rpeff,
        trigger=CronTrigger(day_of_week="wed", hour="12", minute="10"),
        id="rpeff",
        max_instances=1,
        replace_existing=True
    )


    scheduler.start()

#test

