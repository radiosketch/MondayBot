import os
import sys
import logging
import subprocess

from discord import Game, File
from discord.ext import commands, tasks
from utils import get_token, datetime

if os.path.exists('logs/output.log'):
    os.rename('logs/output.log', f'logs/{str(datetime.now()).replace(":", "")}.log')

LOGGER = logging.getLogger('discord')
LOGGER.setLevel(logging.INFO)
formatter = logging.Formatter(fmt='[%(asctime)s][%(levelname)-8s] %(message)s', datefmt='%Y/%m/%d %H:%M:%S')
screen_handler = logging.StreamHandler(stream=sys.stdout)
screen_handler.setFormatter(formatter)
LOGGER.addHandler(screen_handler)
file_handler = logging.FileHandler(f'logs/output.log')
file_handler.setFormatter(formatter)
LOGGER.addHandler(file_handler)
LOGGER.removeHandler(LOGGER.handlers[0])
LOGGER.propagate = False

TOKEN = get_token()

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

    @commands.command()
    @commands.check(is_developer)
    async def logs(self, ctx):
        '''
        Posts the log file in chat
        '''
        await ctx.send(file=File('logs/output.log'))

    @tasks.loop(hours=8)
    async def check_log_size(self):
        self.logger.info('Checking log size...')
        MAX_FOLDER_MEMORY = .1 * 10**7
        cur_memory = 0
        for dirpath, _, filenames in os.walk('logs'):
            for file in filenames:
                cur_memory += os.stat(file).st_size
        percent_usage = (cur_memory / MAX_FOLDER_MEMORY) * 100
        self.logger.info(f'Using {percent_usage}% of log folder memory')
        if percent_usage > 90:
            self.logger.info('Clearing space for more recent log files...')
            for dirpath, _, filenames in os.walk('logs'):
                for file in filenames:
                    self.logger.info(f'Removing {file}...')
                    os.remove(os.path.join(dirpath, file))
            self.logger.info('Done.')
        
    @check_log_size.before_loop
    async def before_check_log_size(self):
        await self.bot.wait_until_ready()

@BOT.event
async def on_ready():
    LOGGER.info(msg=f'{BOT.user.name} is ready')
    await BOT.change_presence(activity=Game("!ping"))
    for channel in BOT.get_all_channels():
        if channel.name == 'general' or channel.name == 'el-general':
            mondays = BOT.get_cog('Mondays')
            if mondays:
                await mondays.set_general(channel)

BOT.add_cog(Developer(BOT, LOGGER))
BOT.load_extension('cogs')

BOT.run(TOKEN)
