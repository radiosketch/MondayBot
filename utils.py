import os
import sys
import logging
import zipfile

import base64
from cryptography.fernet import Fernet

from datetime import datetime, timedelta
from dateutil import parser

new_filepath = 'logs/new.log'
recent_filepath = 'logs/recent.log'

LOGGER = logging.getLogger('discord')
LOGGER.setLevel(logging.DEBUG)
formatter = logging.Formatter(fmt='[%(asctime)s][%(levelname)-8s] %(message)s', datefmt='%Y/%m/%d %H:%M:%S')
screen_handler = logging.StreamHandler(stream=sys.stdout)
screen_handler.setFormatter(formatter)
LOGGER.addHandler(screen_handler)
file_handler = logging.FileHandler(new_filepath)
file_handler.setFormatter(formatter)
LOGGER.addHandler(file_handler)
LOGGER.removeHandler(LOGGER.handlers[0])
LOGGER.propagate = False

def update_filehandler():
    '''
    Force the FileHandler to refocus onto recent_filepath
    '''
    LOGGER.removeHandler(LOGGER.handlers[1])
    file_handler = logging.FileHandler(recent_filepath)
    file_handler.setFormatter(formatter)
    LOGGER.addHandler(file_handler)

def rotate_log():
    if os.path.exists(new_filepath):
        # This is the first time rotate_log has run
        # Not enough time has passed to log relevant info
        os.rename(new_filepath, recent_filepath)
        update_filehandler()
        return

    # Otherwise recent.log has existed since the last rotation
    # Rename recent.log and replace it
    dated_filepath = f'logs/{str(datetime.now()).replace(":", "-").replace(" ", "_")}.log'
    os.rename(recent_filepath, dated_filepath)
    LOGGER.info(f'Renamed {recent_filepath} to {dated_filepath}')
    os.system(f'touch {recent_filepath}')
    update_filehandler()
        
    
def parse_log_name(filename):
    return parser.parse(filename.replace('-', ':').replace('_', ' ')[:-4])

def get_log(oldest=False):
    '''
    Get the newest (default) or oldest file in the log folder
    '''
    search_file = 'January 1st 3000.log' if oldest else 'January 1st 1970.log'
    LOGGER.info(f'Starting the search at {search_file}')
    for dirname, _, filenames in os.walk('logs'):
        for file in filenames:
            filepath = os.path.join(dirname, file)
            if filepath == recent_filepath or filepath == new_filepath:
                if oldest:
                    continue
                return filepath
            LOGGER.info(f'Comparing {search_file} and {file}')
            search_file_date = parse_log_name(search_file)
            file_date = parse_log_name(file)
            if search_file_date > file_date:
                search_file = file
        return os.path.join(dirname, search_file)

def get_log_folder_memory_usage(max_mem=.75 * 10**6):
    cur_mem = 0
    for dirpath, _, filenames in os.walk('logs'):
        for file in filenames:
            LOGGER.info(f'Checking {file}')
            cur_mem += os.stat(os.path.join(dirpath, file)).st_size
    return (cur_mem / max_mem) * 100

def delete_oldest_log():
    os.remove(get_log(oldest=True))

def zipdir(path, name):
    with zipfile.ZipFile(name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for dirpath, _, filenames in os.walk(path):
            for file in filenames:
                zipf.write(os.path.join(dirpath, file), '.')

def get_token():
    return base64.b64decode(Fernet(open('key.txt', 'rb').read()).decrypt(open('encoded.txt', 'rb').read())).decode()

def trim_date(date):
    return parser.parse(date.strftime('%D'))

def get_now():
    return trim_date(datetime.now())

def ordinal(n):
    if n in [11, 12, 13]:
        return str(n) + 'th'
    return str(n) + ['th', 'st', 'nd', 'rd', 'th'][min(4, n % 10)]

def plural_days(n):
    return f'{n} day' if n == 1 else f'{n} days'

def whitelist_exists(ctx):
    LOGGER.info('Checking for whitelist.txt')
    if not os.path.exists('whitelist.txt'):
        LOGGER.info('whitelist.txt does not exist, creating...')
        with open('whitelist.txt', 'x') as f:
            pass
    return True

def get_developers():
    with open('whitelist.txt', 'r') as f:
        devs = [line[:-1] for line in f.readlines()]
        return devs

def add_developer(username):
    with open('whitelist.txt', 'a') as f:
        f.write(f'{username}\n')
    LOGGER.info(f'After adding {username}: {get_developers()}')

def remove_developer(username):
    developers = get_developers()
    os.remove('whitelist.txt')
    whitelist_exists(None)
    for dev in developers:
        if dev != username:
            add_developer(dev)
    LOGGER.info(f'After deleting {username}: {get_developers()}')

def is_developer(ctx):
    LOGGER.info(f'Developer check for {ctx.message.author.name}')
    return ctx.message.author.name in get_developers()

def is_owner(ctx):
    return ctx.message.author.name == '101prairiedogs'

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
