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

        # @aiocron.crontab('* * * * *')
        # async def test():
        #     self.logger.info('Testing aiocrontab')
        #     save_garf('back on the work site no more nagging wife')
        #     await self.send(file='output.jpg')
        # test.start()
        # self.logger.info('Started test crontab')

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

def teardown(bot: commands.Bot):
    bot.remove_cog('Base')
    bot.remove_cog('Mondays')
    LOGGER.info('Removed Cogs')
