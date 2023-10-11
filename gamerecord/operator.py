from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django_apscheduler.jobstores import register_events, DjangoJobStore
from .views import gainrp, resetrp, rpeff


def testop():

    print('testop')
    resetrp()
    gainrp(0,333)
    gainrp(333,666)
    gainrp(666,1000)
    pass

def start():

    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(),'default')
    register_events(scheduler)

    scheduler.add_job(
        testop,
        trigger=CronTrigger(day_of_week="wed", hour="10", minute="50"),
        id="resetrp",
        max_instances=1,
        replace_existing=True
    )
    scheduler.start()

#test

