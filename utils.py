import logging

import base64
from cryptography.fernet import Fernet

from datetime import datetime, timedelta
from dateutil import parser


logging.basicConfig()
logger = logging.getLogger('utils')
logger.setLevel(logging.DEBUG)
logger.disabled = True


def get_token():
    return base64.b64decode(Fernet(open('key.txt', 'rb').read()).decrypt(open('encoded.txt', 'rb').read())).decode()

def trim_date(date):
    return parser.parse(date.strftime('%D'))

def get_now():
    return trim_date(datetime.now())

def ordinal(n):
    last_digit = int(str(n)[-1])
    if last_digit == 1:
        return str(n) + 'st'
    if last_digit == 2:
        return str(n) + 'nd'
    if last_digit == 3:
        return str(n) + 'rd'
    if last_digit >= 4:
        return str(n) + 'th'
    if last_digit == 0:
        return str(n) + 'th'

def plural_days(n):
    return f'{n} day' if n == 1 else f'{n} days'

def is_monday(date):
    return date.weekday() == 0

def generate_next_joke_monday(start_date=parser.parse('July 22nd, 2017'), end_date=None, joke_interval=57):
    if end_date == None:
        end_date = get_now()
    joke_timedelta = timedelta(days=joke_interval)
    joke_monday = start_date
    i = 1
    while joke_monday < end_date:
        joke_monday += joke_timedelta
        i += 1
    return joke_monday, i

def generate_next_real_monday(from_date=None):
    if from_date == None:
        from_date = get_now()
    one_day = timedelta(days=1)
    for i in range(6):
        if is_monday(from_date):
            logger.debug(f'The next real Monday (in {i} days) is {from_date}')
            return from_date, i
        from_date += one_day

def generate_next_super_monday(from_date=None, joke_interval=57):
    if from_date == None:
        from_date = get_now()
    joke_timedelta = timedelta(days=joke_interval)
    monday = False
    while not monday:
        joke_monday, i = generate_next_joke_monday(end_date=from_date)
        monday = is_monday(joke_monday)
        from_date += joke_timedelta
    logger.debug(f'The next super Monday (the {ordinal(i)} joke monday, and the {ordinal((joke_monday - parser.parse("July 22nd, 2017")).days)} day since server creation) is {joke_monday}')
    return joke_monday

def is_joke_monday(day=None):
    if day == None:
        day = get_now()
    joke_monday, i = generate_next_joke_monday()
    return day == joke_monday

def is_real_monday(day=None):
    if day == None:
        day = get_now()
    return is_monday(day)

def is_super_monday(day=None):
    if day == None:
        day = get_now()
    super_monday = generate_next_super_monday()
    return day == super_monday
