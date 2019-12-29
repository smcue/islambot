from aiohttp import ClientSession
from discord.ext import commands
from bs4 import BeautifulSoup
import discord

icon = 'https://www.stickpng.com/assets/images/580b585b2edbce24c47b2abb.png'

class QuranMorphology(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.session = ClientSession(loop = bot.loop)
        self.url = 'http://corpus.quran.com/wordmorphology.jsp?location=({}:{}:{})'

    @commands.command(name="morphology")
    async def morphology(self, ctx, ref: str):

        if not self.isInCorrectFormat(ref):
            await ctx.send('**Invalid arguments!** Do `-quranmorphology surah:verse:word.\n\n'
                               'Example: `-quranmorphology 1:1:2` (for the second word of the first verse of Surah al-Fatiha)')
            return

        try:
            surah, verse, word = ref.split(':')

        except:
            await ctx.send('**Invalid arguments!** Do `-quranmorphology surah:verse:word.`\n\n'
                               'Example: `-morphology 1:1:2` (for the second word of the first verse of Surah al-Fatiha)')
            return

        async with self.session.get(self.url.format(surah, verse, word)) as resp:
            data = await resp.read()

        scanner = BeautifulSoup(data, "html.parser")

        paragraph = scanner.find("p", "first")
        morphology = scanner.find("td", "morphologyCell")
        grammar = scanner.find("td", "grammarCell")
        imageText = scanner.find("a", "tokenLink")
        for image in imageText:
            image = (image['src'])
        em = discord.Embed(colour = 0x761e89)

        em.set_author(name = f"Qurʾān - {surah}:{verse}, Word {word}", icon_url = icon)
        em.add_field(name='Morphology', value = f'{morphology.text} ({grammar.text})', inline = False)
        em.add_field(name='Information', value = f'{paragraph.text}', inline = False)
        em.set_thumbnail(url=f'http://corpus.quran.com{image}')
        await ctx.send(embed=em)

    @staticmethod
    def isInCorrectFormat(ref):
        try:
            ref.split(':')
            return True
        except:
            return False

# Register as cog
def setup(bot):
    bot.add_cog(QuranMorphology(bot))