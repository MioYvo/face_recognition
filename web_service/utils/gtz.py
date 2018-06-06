# coding=utf-8
# __author__ = 'Mio'
from datetime import datetime, time, timedelta, date

import os
from dateutil import parser
from pytz import timezone, utc
from tornado.escape import native_str

UTC_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
SQL_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
UTC_MONTH_FORMAT = '%Y-%m'
DATE_FORMAT = "%Y-%m-%d"

LOCAL_TZ = os.getenv("LOCAL_TZ", "Asia/Shanghai")
local_timezone = timezone(LOCAL_TZ)


def string_2_datetime(_string):
    if isinstance(_string, bytes):
        _string = native_str(_string)
    return parser.parse(_string)


def string_2_date(_string):
    dt = string_2_datetime(_string)
    if dt.tzinfo:
        dt = dt.astimezone(local_timezone)
    else:
        dt = local_timezone.localize(dt)
    return dt.date()


def datetime_2_string(_datetime, _format=UTC_DATETIME_FORMAT):
    return _datetime.strftime(_format)


def datetime_2_isoformat(_dt):
    return _dt.isoformat()


def date_2_string(_date, _format=DATE_FORMAT):
    return _date.strftime(_format)


def isoformat_2_time(_isoformat_str):
    d = parser.parse(_isoformat_str)
    return d.time()


def return_date(day):
    if isinstance(day, datetime):
        return day.date()
    else:
        return day


def date_2_datetime(_date):
    return datetime.combine(_date, time.min)


# def localize_dt(_dt, local_tz=local_timezone):
#     return local_tz.localize(_dt)

def localize_dt(_dt, local_tz=local_timezone):
    if isinstance(_dt, date):
        _dt = datetime.combine(_dt, time.min)
    return local_tz.localize(_dt)


def local_date_2_utc_dt(_date, tz=local_timezone):
    local_dt = tz.localize(datetime.combine(_date, time.min))
    return local_dt.astimezone(utc)


def local_dt_2_utc_dt(_dt, local_tz=local_timezone):
    dt = local_tz.localize(_dt)
    return dt.astimezone(utc)


def utc_now_dt(tz=utc):
    return tz.localize(datetime.utcnow())


def local_now_dt(tz=local_timezone):
    return utc_now_dt().astimezone(tz)


def local_today(tz=local_timezone):
    return local_now_dt(tz=tz).date()


local_yesterday = local_today() - timedelta(days=1)


def utc_now_dt_str():
    return datetime_2_string(utc_now_dt())

# if __name__ == '__main__':
#     from datetime import date
#     _today = date.today()
#     a = date_2_string(_today)
#     b = string_2_date(a)
#
#     print(a, type(a), b, type(b))
