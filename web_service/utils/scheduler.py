# coding=utf-8
# __author__ = 'Mio'
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .singleton import singleton


class NoRunningFilter(logging.Filter):
    def filter(self, record):
        return not (record.msg.startswith('Running job') or record.msg.endswith("executed successfully"))


@singleton
class AScheduler(object):
    def __init__(self, jobstores, job_defaults, JOB_ID, LOCAL_TZ_OBJ, loop,
                 remove_old_jobs=True):
        self.JOB_ID = JOB_ID

        self.timezone = LOCAL_TZ_OBJ

        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            job_defaults=job_defaults,
            timezone=LOCAL_TZ_OBJ,
            event_loop=loop
        )

        if remove_old_jobs:
            self.scheduler.remove_all_jobs()
            self.job_ids = set()
        else:
            self.job_ids = {job.id for job in self.scheduler.get_jobs()}

    def start(self, logging_running_job_state=False):
        self.scheduler.start()
        logging.info(self.scheduler.get_jobs())
        if not logging_running_job_state:
            # noinspection PyProtectedMember
            self.scheduler._executors['default']._logger.addFilter(NoRunningFilter())

    def add_cron_job(self, func, func_kwargs, year=None, month=None, day=None, week=None,
                     day_of_week=None, hour=None, minute=None, second=None):
        """
        If you schedule jobs in a persistent job store during your application’s initialization,
        you MUST define an explicit ID for the job and use replace_existing=True
        or you will get a new copy of the job every time your application restarts!

        :param func_kwargs:
        :param func: function to execute cron
        :param year (int|str) – 4-digit year
        :param month (int|str) – month (1-12)
        :param day (int|str) – day of the (1-31)
        :param week (int|str) – ISO week (1-53)
        :param day_of_week (int|str) – number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
        :param hour (int|str) – hour (0-23)
        :param minute (int|str) – minute (0-59)
        :param second (int|str) – second (0-59)

        :return:
        """
        job_id = self.JOB_ID.format(func=func.__name__)
        job = self.scheduler.add_job(
            func=func,
            kwargs=func_kwargs,
            id=job_id,
            replace_existing=True,
            trigger='cron', year=year, month=month, day=day, week=week,
            day_of_week=day_of_week, hour=hour, minute=minute, second=second,
            timezone=self.timezone
        )
        self.job_ids.add(job.id)
        return job

    def stop(self):
        # self.scheduler.remove_all_jobs()

        # shutdown method will close mongo connection
        self.scheduler.shutdown()
