import os
import subprocess

from discord import Game, File
from discord.ext import commands, tasks
from utils import LOGGER, get_token, rename_log, get_log, get_log_folder_memory_usage, delete_oldest_log


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
        await ctx.send(file=File(get_log()))

    @tasks.loop(hours=8)
    async def check_log_size(self):
        self.logger.info('Renaming old log file...')
        # TODO Testing on Windows shows that the recent.log file is open, blocking renaming
        rename_log()
        self.logger.info('Calculating log folder usage...')
        percent_usage = get_log_folder_memory_usage()
        self.logger.info(f'Using {percent_usage}% of log folder memory')
        if percent_usage > 80:
            self.logger.info('Clearing space for more recent log files...')
            delete_oldest_log()
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


if __name__ == '__main__':
    BOT = commands.Bot(command_prefix="!")

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
    BOT.run(get_token())
    
