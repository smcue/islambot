from discord.ext import commands
from aiohttp import ClientSession
from helpers import convertToArabicNumber
import discord

icon = 'https://cdn6.aptoide.com/imgs/6/a/6/6a6336c9503e6bd4bdf98fda89381195_icon.png'

invalid_format = "**Please type the command in this format**: `-mushaf <surah>:<ayah>`" \
        "\ne.g. `-mushaf 112:1` \nFor a color-coded mushaf, added 'tajweed' to the end " \
        "of the command\ne.g. `-mushaf 112:1 tajweed`"

invalid_verse = '**Verse could not be found**. Please check the verse exists, or try again later.'


class Mushaf(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.session = ClientSession(loop=bot.loop)

    @commands.command(name="mushaf")
    async def mushaf(self, ctx, ref: str, tajweed : str = 'none'):

        try:
            surah, ayah = ref.split(':')
        except ValueError:
            return await ctx.send(invalid_format)

        async with self.session.get(f'https://api.alquran.cloud/ayah/{surah}:{ayah}') as resp:
            if resp.status != 200:
                return await ctx.send(invalid_verse)
            data = await resp.json()
            page = data['data']['page']

        if page < 10:
            formatted_page = '00' + str(page)
        elif page < 100:
            formatted_page = '0' + str(page)
        else:
            formatted_page = str(page)

        if tajweed is 'none':
            url = f'https://www.searchtruth.org/quran/images2/large/page-{formatted_page}.jpeg'
        else:
            url = f'https://www.searchtruth.org/quran/images1/{formatted_page}.jpg'

        arabic_page_number = convertToArabicNumber(str(page))
        em = discord.Embed(title=f'Page {page}'
                                 f'\n  الصفحة{arabic_page_number}', colour=0x006400)
        em.set_author(name=f'Mushaf / مصحف', icon_url=icon)
        em.set_image(url=url)
        await ctx.send(embed=em)


# Register as cog
def setup(bot):
    bot.add_cog(Mushaf(bot))
