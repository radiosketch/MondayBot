import logging
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
        self.just_started = True
        self.check_date.start()
        self.general = None
        self.logger.info('Mondays Cog is initialized')

    async def set_general(self, channel):
        self.general = channel
        self.logger.info(f'Set #general: {self.general}')

    async def send(self, **kwargs):
        await self.general.send(**kwargs)

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
        embed = Embed(
            color=Color.from_rgb(104, 237, 198),
        )
        save_garf(f'''{"It's Monday!" if utils.is_real_monday() else f"The next Monday is {real_monday.strftime('%m/%d/%Y')}, in {utils.plural_days(days_to_real_monday)}, "}\n{"and it's also a Super Monday!" if utils.is_super_monday() else f"and the next Super Monday is {super_monday.strftime('%m/%d/%Y')}, in {(super_monday - utils.get_now()).days} days"}\n''', align='left')
        embed.set_image(url='attachment://output.jpg')
        await ctx.send(file=File('output.jpg'), embed=embed)

    @info.error
    async def info_error(ctx, error):
        await ctx.send(error)
        
    @tasks.loop(minutes=30)
    async def check_date(self):
        now = utils.datetime.now()
        if now.hour != 7 or not now.minute > 30:
            # Return if the time is not 7:30am - 7:59am
            if self.just_started:
                self.logger.info('Waiting for 7:30am...')
            self.just_started = False
            return
        is_real_monday = utils.is_real_monday()
        self.logger.info(f'Today {"is" if is_real_monday else "is not"} a real Monday')
        if is_real_monday:
            save_garf('back on the work site no more nagging wife')
            self.send(file=File('output.jpg'))
        is_joke_monday = utils.is_joke_monday()
        self.logger.info(f'Today {"is" if is_joke_monday else "is not"} a joke Monday')
        if is_joke_monday:
            save_garf('back on the work site wife died of 57 bullets to the chest')
            self.send(file=File('output.jpg'))
        is_super_monday = utils.is_super_monday()
        self.logger.info(f'Today {"is" if is_super_monday else "is not"} a super Monday')
        if is_super_monday:
            save_garf('It\'s a motha fuckin SUPA MONDAY lets GOOOO BABEEEE')
            self.send(file=File('output.jpg'))

    @check_date.before_loop
    async def before_check_date(self):
        await self.bot.wait_until_ready()

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
