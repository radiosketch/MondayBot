import os
import subprocess
import logging
import aiocron
import utils
from garfutils import save_garf
from discord import Embed, Color, File
from discord.ext import commands, tasks

LOGGER = logging.getLogger('discord')
LOGGER.setLevel(logging.INFO)

class Base(commands.Cog):
    def __init__(self, bot: commands.Bot, logger):
        self.bot = bot
        self.logger = logger
        self.logger.info('Base Cog is initialized')
    
    @commands.command()
    async def ping(self, ctx):
        await ctx.send('Pong!')
        
from utils import get_token, is_owner, is_developer, 
whitelist_exists, add_developer, remove_developer, 
rotate_log, get_log, get_log_folder_memory_usage, 
delete_oldest_log, filter_user_input_as_filepath

class Developer(commands.Cog):
    def __init__(self, bot: commands.Bot, logger):
        self.bot = bot
        self.logger = logger
        self.check_log_size.start()
        self.logger.info('Developer Cog is initialized')

    @commands.command()
    @commands.check(is_owner)
    async def stop(self, ctx):
        '''
        Owner only
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
        await ctx.send(f'```{result}```')

    @commands.command()
    @commands.check(is_developer)
    async def logs(self, ctx):
        '''
        Posts the log file in chat
        '''
        await ctx.send(file=File(get_log()))

    @tasks.loop(hours=8)
    async def check_log_size(self):
        rotate_log()
        self.logger.info('Calculating log folder usage...')
        percent_usage = get_log_folder_memory_usage()
        self.logger.info(f'Using {percent_usage}% of log folder memory')
        if percent_usage > 80:
            self.logger.info('Clearing space for more recent log files...')
            while percent_usage > 80:
                delete_oldest_log()
                percent_usage = get_log_folder_memory_usage()
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

    
    @commands.command()
    @commands.check(is_owner)
    @commands.check(whitelist_exists)
    async def whitelist(self, ctx):
        '''
        Owner Only
        ''' 
        new_username = ctx.message.content[11:]
        if new_username != '':
            add_developer(new_username)
            self.logger.info(f'Added \'{new_username}\' to the whitelist')
        result = str(subprocess.check_output(['cat', 'whitelist.txt'], stderr=subprocess.STDOUT), encoding='utf-8')
        self.logger.info(f'\n# whitelist.txt\n{result}')
        await ctx.send(f'```py\n# whitelist.txt\n{result}```')

    
    @commands.command()
    @commands.check(is_owner)
    @commands.check(whitelist_exists)
    async def unwhitelist(self, ctx):
        '''
        Owner Only
        '''
        username = ctx.message.content[13:]
        if username != '':
            remove_developer(username)
            self.logger.info(f'Removed \'{username}\' from the whitelist')
        result = str(subprocess.check_output(['cat', 'whitelist.txt'], stderr=subprocess.STDOUT), encoding='utf-8')
        self.logger.info(f'\n# whitelist.txt\n{result}')
        await ctx.send(f'```py\n# whitelist.txt\n{result}```')


    @commands.command()
    @commands.check(is_developer)
    async def ls(self, ctx):
        '''
        <directory> Lists source directories and files
        '''
        # TODO perform strict checks on user inputs
        # input string MUST be a valid filepath
        directory = filter_user_input_as_filepath(ctx.message.content[4:])
        if not directory:
            await ctx.send('Invalid input. The string must not contain spaces or \'..\'')
            return
        try:
            result = str(subprocess.check_output(['ls', '-a', directory], stderr=subprocess.STDOUT), encoding='utf-8')
            self.logger.info(f'!ls used on {directory}')
            await ctx.send(f'```{result}```')
        except Exception as e:
            self.logger.error(e)
            await ctx.send(f'```{e}```')
        

    @commands.command()
    @commands.check(is_developer)
    async def download(self, ctx):
        '''
        <filepath> Download a source file
        '''
        # TODO perform strict checks on user inputs
        # input string MUST be a valid filepath
        filepath = filter_user_input_as_filepath(ctx.message.content[10:])
        if not filepath:
            await ctx.send('Invalid input. The string must not contain spaces or \'..\'')
            return
        try:
            await ctx.send(file=File(filepath))
        except FileNotFoundError as e:
            self.logger.error(e)
            await ctx.send(f'FileNotFound: {filepath}')
        except IsADirectoryError as e:
            self.logger.warning(e)
            await ctx.send('Cannot download entire directories. Check out my GitHub!\nhttps://github.com/radiosketch/MondayBot')


class Mondays(commands.Cog):
    def __init__(self, bot: commands.Bot, logger):
        self.bot = bot
        self.logger = logger
        self.general = []
        self.logger.info('Mondays Cog is initialized')

        @aiocron.crontab('30 7 * * 1')
        async def on_monday():
            self.logger.info('It\'s Monday!')
            is_joke = utils.is_joke_monday()
            is_super = utils.is_super_monday()
            
            save_garf('back on the work site no more nagging wife')
            await self.send(file='output.jpg')

            if is_joke:
                self.logger.info('It\'s a Joke Monday')
                # TODO
            else:
                self.logger.info('It\'s not a Joke Monday')

            if is_super:
                self.logger.info('It\'s a Super Monday!')
                # TODO
            else:
                self.logger.info('It\'s not a Super Monday')
        on_monday.start()
        self.logger.info('Started on_monday crontab')

    async def add_general(self, channel):
        self.general.append(channel)
        self.logger.info(f'Added #general: {channel}')

    async def send(self, **kwargs):
        try:
            for general in self.general:
                with open(kwargs['file'], 'rb') as f:
                    await general.send(file=File(f))
        except KeyError as e:
            print(f'KeyError in Mondays.send: {e}')

    @commands.command()
    async def garf(self, ctx):
        '''
        <text> : Make your own 'I Love Mondays' meme
        '''
        save_garf(ctx.message.content[6:])
        await ctx.send(file=File('output.jpg'))
    
    @commands.command()
    async def garfhate(self, ctx):
        '''
        <text> : Make your own 'I Hate Mondays' meme
        '''
        save_garf(ctx.message.content[10:], hate=True)
        await ctx.send(file=File('output.jpg'))
    
    @commands.command()
    async def info(self, ctx):
        '''
        Provides information about future Mondays
        '''
        real_monday, days_to_real_monday = utils.generate_next_real_monday()
        # joke_monday, nth_joke_monday = utils.generate_next_joke_monday()
        super_monday = utils.generate_next_super_monday()
        save_garf(f'''{"It's Monday!" if utils.is_real_monday() else f"The next Monday is {real_monday.strftime('%m/%d/%Y')}, in {utils.plural_days(days_to_real_monday)}, "}\n{"and it's also a Super Monday!" if utils.is_super_monday() else f"and the next Super Monday is {super_monday.strftime('%m/%d/%Y')}, in {(super_monday - utils.get_now()).days} days"}\n''', align='left')
        await ctx.send(file=File('output.jpg'))

    def cog_unload(self):
        self.check_date.cancel()
        self.logger.info('Cancelled check_date loop')

def setup(bot: commands.Bot):
    LOGGER.info('Adding Cogs...')
    bot.add_cog(Base(bot, LOGGER))
    bot.add_cog(Mondays(bot, LOGGER))
    bot.add_cog(Developer(bot, LOGGER))

def teardown(bot: commands.Bot):
    bot.remove_cog('Base')
    bot.remove_cog('Mondays')
    bot.remove_cog('Developer')
    LOGGER.info('Removed Cogs')
