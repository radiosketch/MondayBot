import os
import subprocess

from discord import Game, File
from discord.ext import commands, tasks
from utils import LOGGER, get_token, is_owner, is_developer, whitelist_exists, add_developer, remove_developer, rename_log, get_log, get_log_folder_memory_usage, delete_oldest_log


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
        self.logger.info('Renaming old log file...')
        # TODO Testing on Windows shows that the recent.log file is open, blocking renaming
        # This issue doesn't seem to arise on Raspbian
        rename_log()
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
    @commands.check(is_owner)
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
        username = ctx.message.content[13:]
        if username != '':
            remove_developer(username)
            self.logger.info(f'Removed \'{username}\' from the whitelist')
        result = str(subprocess.check_output(['cat', 'whitelist.txt'], stderr=subprocess.STDOUT), encoding='utf-8')
        self.logger.info(f'\n# whitelist.txt\n{result}')
        await ctx.send(f'```py\n# whitelist.txt\n{result}```')


    @commands.command()
    @commands.check(is_owner)
    async def bash(self, ctx):
        '''
        Access the host terminal
        '''
        command = ctx.message.content[6:].split(' ')
        self.logger.info(f'Executing {command}')
        try:
            result = str(subprocess.check_output(command, stderr=subprocess.STDOUT), encoding='utf-8')
            self.logger.info(f'\n# bash\n{result}')
            await ctx.send(f'```bash\n$ bash\n{result}```')
        except Exception as e:
            self.logger.error(e)
            await ctx.send(f'```bash\n$ bash\n{error}```')


if __name__ == '__main__':
    BOT = commands.Bot(command_prefix="!")

    @BOT.event
    async def on_ready():
        LOGGER.info(msg=f'{BOT.user.name} is ready')
        await BOT.change_presence(activity=Game("!help"))
        for channel in BOT.get_all_channels():
            if channel.name == 'general' or channel.name == 'el-general':
                mondays = BOT.get_cog('Mondays')
                if mondays:
                    await mondays.set_general(channel)

    BOT.add_cog(Developer(BOT, LOGGER))
    BOT.load_extension('cogs')
    BOT.run(get_token())
    
