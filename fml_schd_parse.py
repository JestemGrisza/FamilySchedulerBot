import logging
import re
import datetime
import pytz

import fml_schd_const
from fml_schd_const import DAY_NAME_FULL, DAY_NAME_3CHAR, DAY_NAME_2CHAR, DATE_REGEXP_SHORT, DATE_REGEXP_LONG, \
    TIME_REGEXP_LONG, TIME_REGEXP_SHORT, DEFAULT_TASK_DURATION


# from datetime import date, datetime, timedelta


def _get_now_formatted() -> str:
    """Возвращает сегодняшнюю дату строкой"""
    return _get_now_datetime().strftime("%Y-%m-%d %H:%M:%S")


def _get_now_datetime() -> datetime.datetime:
    """Возвращает сегодняшний datetime с учётом времненной зоны"""
    tz = pytz.timezone("Europe/Kiev")
    now = datetime.datetime.now(tz)
    return now


def today():
    return datetime.date.today()


def yesterday():
    return today() - datetime.timedelta(days=1)


def tomorrow():
    return today() + datetime.timedelta(days=1)


def year():
    return datetime.date.today().year


def next_weekday(d, weekday):
    """https://stackoverflow.com/questions/6558535/find-the-date-for-the-first-monday-after-a-given-date"""
    # d = datetime.date(2011, 7, 2)
    # next_monday = next_weekday(d, 0) # 0 = Monday, 1=Tuesday, 2=Wednesday...
    # print(next_monday)

    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)


"""
ACHTUNG!!!! WARNING!!!! POZOR!!!! UWAGA!!!!
Accept from user DATE in reverse format dd-mm-yyyy (short: dd-mm) instead Datetime yyyy-mm-dd !!!
In DB and output uses Datetime yyyy-mm-dd !!!
"""


def is_day(token: str):
    start_date = ''
    token = token.lower()
    # Check 0 arg is day of week
    if token in DAY_NAME_FULL:
        weekday = DAY_NAME_FULL.index(token)
        start_date = next_weekday(today(), weekday)
    elif token in DAY_NAME_2CHAR:
        weekday = DAY_NAME_2CHAR.index(token)
        start_date = next_weekday(today(), weekday)
    elif token in DAY_NAME_3CHAR:
        weekday = DAY_NAME_3CHAR.index(token)
        start_date = next_weekday(today(), weekday)
    # Check 0 arg is date
    elif re.match(DATE_REGEXP_LONG, token):
        start_date_lst = re.sub("[/.]", "-", token).split('-')
        start_date = f"{start_date_lst[2]}-{start_date_lst[1]}-{start_date_lst[0]}"
    # Check 0 arg is date
    elif re.match(DATE_REGEXP_SHORT, token):
        start_date_lst = re.sub("[/.]", "-", token).split('-')
        start_date = f"{year()}-{start_date_lst[1]}-{start_date_lst[0]}"
    # Check 0 arg is tomorrow
    elif token == 'tomorrow':
        start_date = tomorrow()
    return start_date


def go(args: str):
    start_date = ''
    start_time = ''
    end_date = ''
    end_time = ''
    task_name = ''
    args_list = args.split(' ')

    if is_day(str(args_list[0])):
        start_date = is_day(str(args_list[0]))
        # print(start_date)
        args_list.pop(0)
    else:
        start_date = today()

    if re.match(TIME_REGEXP_LONG, args_list[0]):
        start_time = args_list[0]
        task_name = ' '.join(args_list[1:]).strip()
    elif re.match(TIME_REGEXP_SHORT, args_list[0]):
        start_time = args_list[0] + ":00"
        task_name = ' '.join(args_list[1:]).strip()

    elif str(args_list[0]).lower() == 'at':
        if re.match(TIME_REGEXP_LONG, args_list[1]):
            # start_date = today()
            start_time = args_list[1]
            task_name = ' '.join(args_list[2:]).strip()
        elif re.match(TIME_REGEXP_SHORT, args_list[1]):
            # start_date = today()
            start_time = args_list[1] + ":00"
            task_name = ' '.join(args_list[2:]).strip()

    elif str(args_list[0]).lower() == 'from':
        if re.match(TIME_REGEXP_LONG, args_list[1]):
            # start_date = today()
            start_time = args_list[1]
        elif re.match(TIME_REGEXP_SHORT, args_list[1]):
            # start_date = today()
            start_time = args_list[1] + ":00"

        if str(args_list[2]).lower() == 'till':
            if re.match(TIME_REGEXP_LONG, args_list[3]):
                end_date = start_date
                end_time = args_list[3]
                task_name = ' '.join(args_list[4:]).strip()
            elif re.match(TIME_REGEXP_SHORT, args_list[3]):
                end_date = start_date
                end_time = args_list[3] + ":00"
                task_name = ' '.join(args_list[4:]).strip()
        else:
            task_name = ' '.join(args_list[3:]).strip()

    start_str = f"{start_date} {start_time}"
    start_datetime = datetime.datetime.strptime(start_str, '%Y-%m-%d %H:%M')

    if end_date == '' or end_time == '':
        """
        If end date and end time not defined -- use DEFAULT_TASK_DURATION
        """
        stop_datetime = start_datetime + datetime.timedelta(minutes=DEFAULT_TASK_DURATION)
    else:
        stop_str = f"{end_date} {end_time}"
        # print(stop_str)
        stop_datetime = datetime.datetime.strptime(stop_str, '%Y-%m-%d %H:%M')

    # return f'Start: {start_date} at {start_time}\nEnd: {end_date} at {end_time}\nTask: {task_name}'
    return start_datetime, stop_datetime, task_name


if __name__ == '__main__':
    print(go('25.11.2021 from 18:01 till 20:11 to cinema'))
