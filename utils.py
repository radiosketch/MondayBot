import os
import sys
import logging

import base64
from cryptography.fernet import Fernet

from datetime import datetime, timedelta
from dateutil import parser

# TODO Consider making a get_logger method
LOGGER = logging.getLogger('discord')
LOGGER.setLevel(logging.DEBUG)
formatter = logging.Formatter(fmt='[%(asctime)s][%(levelname)-8s] %(message)s', datefmt='%Y/%m/%d %H:%M:%S')
screen_handler = logging.StreamHandler(stream=sys.stdout)
screen_handler.setFormatter(formatter)
LOGGER.addHandler(screen_handler)
file_handler = logging.FileHandler(f'logs/recent.log')
file_handler.setFormatter(formatter)
LOGGER.addHandler(file_handler)
LOGGER.removeHandler(LOGGER.handlers[0])
LOGGER.propagate = False

def rename_log():
    recent = 'logs/recent.log'
    if os.path.exists(recent):
        new_name = f'logs/{str(datetime.now()).replace(":", "-")}.log'
        try:
            os.rename(recent, new_name)
            LOGGER.info(f'Renamed {recent} to {new_name}')
        except Exception as e:
            LOGGER.error(e)
        
    
def parse_log_name(filename):
    return parser.parse(filename.replace('-', ':')[:-4])

def get_log(oldest=False):
    '''
    Get the newest (default) or oldest file in the log folder
    '''
    search_log = 'January 1st 3000.log' if oldest else 'January 1st 1970.log'
    LOGGER.info(f'Starting the search at {search_log}')
    for dirname, _, filenames in os.walk('logs'):
        for file in filenames:
            LOGGER.info(f'Comparing {search_log} and {file}')
            if not oldest and file == 'recent.log':
                return file
            search_log_date = parse_log_name(search_log)
            file_date = parse_log_name(file)
            if oldest and search_log_date > file_date:
                search_log = file
            elif search_log_date < file_date:
                search_log = file
        return os.path.join(dirname, search_log)

def get_log_folder_memory_usage(max_mem=.75 * 10**6):
    cur_mem = 0
    for dirpath, _, filenames in os.walk('logs'):
        for file in filenames:
            LOGGER.info(f'Checking {file}')
            cur_mem += os.stat(os.path.join(dirpath, file)).st_size
    return (cur_mem / max_mem) * 100

def delete_oldest_log():
    os.remove(get_log(oldest=True))

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
    for i in range(7):
        if is_monday(from_date):
            LOGGER.debug(f'The next real Monday (in {i} days) is {from_date}')
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
    LOGGER.debug(f'The next super Monday (the {ordinal(i)} joke monday, and the {ordinal((joke_monday - parser.parse("July 22nd, 2017")).days)} day since server creation) is {joke_monday}')
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
