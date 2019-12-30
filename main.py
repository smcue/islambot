from helpers import prefix
import discord

description = "An Islamic bot for Discord."
bot = discord.ext.commands.Bot(command_prefix=prefix, description=description)


@bot.event
async def on_ready():

    print(f'Logged in as {bot.user.name} ({bot.user.id}) on {len(bot.guilds)} servers')
    game = discord.Game(f"-ihelp | {len(bot.guilds)} servers")
    await bot.change_presence(activity=game)

    bot.remove_command('help')

    cog_list = ['hadith', 'hijricalendar', 'prayertimes', 'quran-morphology', 'quran', 'tafsir', 'tafsir-english', 'mushaf', "search", 'help']
    for cog in cog_list:
        bot.load_extension(cog)

token = open("token.txt", "r").read()
bot.run(token.strip())

