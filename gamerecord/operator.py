from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django_apscheduler.jobstores import register_events, DjangoJobStore
from .views import gainrp, resetrp, rpeff

def testopop():
    resetrp()
    gainrp(0,333)
    rpeff()
    pass

def start():

    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(),'default')
    scheduler.add_job(
        testopop,
        trigger=CronTrigger(day_of_week="wed", hour="11", minute="52"),
        id="resetrp",
        max_instances=1,
        replace_existing=True
    )

    scheduler.start()

#test

