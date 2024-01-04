from discord import Game, File
from discord.ext import commands, tasks
        
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
                    await mondays.add_general(channel)
                    
    BOT.load_extension('cogs')
    BOT.run(get_token())
    
