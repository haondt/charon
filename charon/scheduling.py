import sched, time, math
from typing import Callable
from croniter import croniter
from dataclasses import dataclass
import logging
from datetime import timedelta
import re, signal

_logger = logging.getLogger(__name__)

class TimeoutError(Exception):
    def __init__(self, message):
        super().__init__(message)

def timeout_handler(job_timeout_seconds: int):
    def inner(signum, frame):
        nonlocal job_timeout_seconds
        raise TimeoutError(f'Job failed to complete in the maximum allowed timeframe: {job_timeout_seconds} seconds')
    return inner

@dataclass
class Job:
    name: str
    itr: Callable[[], float]
    task: Callable
    repeat: bool = True
    timeout_seconds: int | None = None

    def schedule_next(self, scheduler):
        next = self.itr()
        now = time.time()

        # prevent iteration from falling behind
        if self.repeat:
            while next < now:
                next = self.itr()

        scheduler.enterabs(next, 1, self.run_and_reschedule, (scheduler,))

    def run_and_reschedule(self, scheduler):
        log_extra = {
            "charon.name": self.name
        }
        _logger.info("Executing job", extra=log_extra)

        if self.timeout_seconds is not None:
            signal.signal(signal.SIGALRM, timeout_handler(self.timeout_seconds))
            try:
                self.task()
            except Exception as e:
                _logger.exception(f"Job failed", extra=log_extra | {
                    "charon.error": str(e)
                })
            finally:
                signal.alarm(0)
        else:
            try:
                self.task()
            except Exception as e:
                _logger.exception(f"Job failed", extra=log_extra | {
                    "charon.error": str(e)
                })

        if self.repeat:
            self.schedule_next(scheduler)

class TimeDeltaIterator:
    def __init__(self, delta: timedelta, base: float):
        self.delta: float = delta.total_seconds()
        self.base = base

    def get_next(self):
        self.base += self.delta
        return self.base


class SchedulerFactory:
    def __init__(self):
        self._job_factories: list[Callable[[], Job]] = []

    def add_cron(self, name: str, task: Callable, crontab: str, timeout: str|None=None):
        itr = croniter(crontab, time.time())
        timeout_seconds = None if timeout is None else int(math.ceil(self._parse_time_delta(timeout).total_seconds()))
        job_factory = lambda: Job(name, itr.get_next, task, timeout_seconds=timeout_seconds)
        self._job_factories.append(job_factory)

    def _parse_time_delta(self, s: str):
        time_re = re.compile(r"^(?:(?P<d>[0-9]+)d)?(?:(?P<h>[0-9]+)h)?(?:(?P<m>[0-9]+)m)?(?:(?P<s>[0-9]+)s)?$")
        time_match = time_re.match(s)
        if time_match is None:
            raise ValueError(f'unable to parse timedelta string {s}')

        gd = time_match.groupdict()
        return timedelta(
            days=int(gd['d'] or 0),
            hours=int(gd['h'] or 0),
            minutes=int(gd['m'] or 0),
            seconds=int(gd['s'] or 0)
        )

    def add_once(self, name: str, task: Callable, delay: str, timeout: str|None=None):
        period = self._parse_time_delta(delay)
        itr = TimeDeltaIterator(period, time.time())
        timeout_seconds = None if timeout is None else int(math.ceil(self._parse_time_delta(timeout).total_seconds()))
        job_factory = lambda: Job(name, itr.get_next, task, False, timeout_seconds=timeout_seconds)
        self._job_factories.append(job_factory)

    def add_every(self, name: str, task: Callable, delay: str, timeout: str|None=None):
        period = self._parse_time_delta(delay)
        itr = TimeDeltaIterator(period, time.time())
        timeout_seconds = None if timeout is None else int(math.ceil(self._parse_time_delta(timeout).total_seconds()))
        job_factory = lambda: Job(name, itr.get_next, task, timeout_seconds=timeout_seconds)
        self._job_factories.append(job_factory)

    def build(self):
        scheduler = sched.scheduler(time.time)
        for jf in self._job_factories:
            job = jf()
            job.schedule_next(scheduler)
        return scheduler
