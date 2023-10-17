import os
import sys
import logging
import subprocess

from discord import Game, File
from discord.ext import commands, tasks
from utils import get_token, datetime, parser

def rename_log():
    if os.path.exists('logs/recent.log'):
        os.rename('logs/recent.log', f'logs/{str(datetime.now()).replace(":", "-")}.log')

def parse_log_name(filename):
    return parser.parse(filename.replace('-', ':')[:-4])

def get_newest_log():
    newest_log = 'January 1st 1970.log'
    for dirname, _, filenames in os.walk('logs'):
        for file in filenames:
            if file == 'recent.log':
                return file
            if parse_log_name(newest_log) < parse_log_name(file):
                newest_log = file
        return os.path.join(dirname, newest_log)


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

BOT = commands.Bot(command_prefix="!")

def is_developer(ctx):
    return ctx.message.author.name == '101prairiedogs'

class Developer(commands.Cog):
    def __init__(self, bot: commands.Bot, logger):
        self.bot = bot
        self.logger = logger
        self.check_log_size.start()
        self.logger.info('Developer Cog is initialized')

    @commands.command()
    @commands.check(is_developer)
    async def stop(self, ctx):
        '''
        Stops the bot
        '''
        await ctx.message.add_reaction('👍')
        await self.bot.close()

    @commands.command()
    @commands.check(is_developer)
    async def reload(self, ctx):
        '''
        Pulls changes from Github and reloads extensions
        '''
        self.logger.info('Reloading...')
        result = str(subprocess.check_output(['git', 'pull'], stderr=subprocess.STDOUT), encoding='utf-8').replace('\n', '')
        self.logger.info(result)
        self.bot.reload_extension('cogs')
        self.logger.info('Done reloading.')
        await ctx.message.add_reaction('👍')
        await ctx.send(f'```{result}```')

    @commands.command()
    @commands.check(is_developer)
    async def logs(self, ctx):
        '''
        Posts the log file in chat
        '''
        await ctx.send(file=File(get_newest_log()))

    @tasks.loop(hours=8)
    async def check_log_size(self):
        self.logger.info('Renaming old log file...')
        rename_log()
        self.logger.info('Calculating log folder usage...')
        MAX_FOLDER_MEMORY = .75 * 10**6
        cur_memory = 0
        for dirpath, _, filenames in os.walk('logs'):
            for file in filenames:
                self.logger.info(f'Checking {file}')
                cur_memory += os.stat(os.path.join(dirpath, file)).st_size
        percent_usage = (cur_memory / MAX_FOLDER_MEMORY) * 100
        self.logger.info(f'Using {percent_usage}% of log folder memory')
        if percent_usage > 80:
            self.logger.info('Clearing space for more recent log files...')
            oldest_log = 'January 1st 3000.log'
            for dirpath, _, filenames in os.walk('logs'):
                for file in filenames:
                    if file == 'recent.log':
                        continue
                    log_date = parse_log_name(file)
                    if log_date < parse_log_name(oldest_log):
                        oldest_log = file
                self.logger.info(f'Removing {oldest_log}...')
                os.remove(os.path.join(dirpath, oldest_log))
            self.logger.info('Done.')
        
    @check_log_size.before_loop
    async def before_check_log_size(self):
        await self.bot.wait_until_ready()

    @commands.command()
    @commands.check(is_developer)
    async def reboot(self, ctx):
        '''
        Reboots the host server
        '''
        await ctx.send('Rebooting... this may take a couple minutes')
        os.system('reboot')

@BOT.event
async def on_ready():
    LOGGER.info(msg=f'{BOT.user.name} is ready')
    await BOT.change_presence(activity=Game("!ping"))
    for channel in BOT.get_all_channels():
        if channel.name == 'general' or channel.name == 'el-general':
            mondays = BOT.get_cog('Mondays')
            if mondays:
                await mondays.set_general(channel)

if __name__ == '__main__':
    BOT.add_cog(Developer(BOT, LOGGER))
    BOT.load_extension('cogs')
    BOT.run(get_token())
    
