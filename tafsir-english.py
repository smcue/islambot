from discord.ext import commands
import discord
import textwrap
import requests
from bs4 import BeautifulSoup
from aiohttp import ClientSession

icon = 'https://lh5.ggpht.com/lRz25mOFrRL42NuHtuSCneXbWV2Gtm7iYZ5eQbuA7JWUC3guWaTaQxNJ7j9rsRMCNAU=w150'

dictName = {
    'ibnkathir': 'Tafsīr Ibn Kathīr',
    'jalalayn': 'Tafsīr al-Jalālayn',
    'tustari': 'Tafsīr al-Tustarī',
    'kashani': 'Tafsīr ʿAbd al-Razzāq al-Kāshānī',
    'qushayri': 'Laṭāʾif al-Ishārāt',
    'wahidi': 'Asbāb al-Nuzūl',
    'kashf': 'Kashf al-Asrār'
}

dictID = {
    'tustari': 93,
    'kashani': 107,
    'qushayri': 108,
    'wahidi': 86,
    'kashf': 109,
}

tags = []

class TafsirEnglish(commands.Cog):
    fields = []

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='tafsir')
    async def tafsir(self, ctx, ref: str, tafsir: str = "jalalayn", page: str = 1):

        try:
            surah, ayah = ref.split(':')

        except:
            await ctx.send("**Invalid verse.** Please type the command in this format: `-tafsir surah:ayah tafsirname`.\n\ne.g. `-tafsir 1:1 ibnkathir`")
            return

        try:
            tafsirName = dictName[tafsir.lower()]

        except:
            await ctx.send("**Couldn't find tafsir!** Please choose from the following: `ibnkathir`, `jalalayn`, `qushayri`, `wahidi`, `tustari`, `kashf`.")
            return


        if tafsir == 'ibnkathir':

            site = requests.get(f'http://www.alim.org/library/quran/AlQuran-tafsir/TIK/{surah}/{ayah}').content
            soup = BeautifulSoup(site, 'html.parser')

            for tag in soup.findAll('p'):
                tags.append(f"{tag.getText()}")
            for tag in soup.findAll('div', {'class':'view-empty'}):
                tags.append(f"{tag.getText()}")

            text = ''.join(tags)
            text = text.replace("Thanks for visiting Alim.org, The Alim Foundation's flagship site that provides the world's only social network built around Qur'an, Hadith, and other classical sources of Islamic knowledge.",'')
            text = text.replace("We are a free service run by many volunteers and we need your help to stay that way. Please consider a small donation(tax-deductible in the USA) to help us improve Alim.org by adding more content and getting faster servers.", '')
            text = text.replace("Share your thoughts about this with others by posting a comment. Visit our FAQ for some ideas.", '')
            text = text.replace('`', 'ʿ')
            text = text.replace('﴾', '')
            text = text.replace('﴿', '')
            text = text.replace('»', '» ')
            text = text.replace('«', ' «')
            text = text.replace('bin', 'b. ')
            text = text.replace('Hadith', 'hadith')
            text = text.replace('No Comments', '')
            text = text.replace('Messenger of Allah', 'Messenger of Allah ﷺ')
            text = text.replace (' )', ')')

            tags.clear()

            processedText = textwrap.wrap(text, 5950, break_long_words=False)
            for entry in processedText:
                em = discord.Embed(title=f'{surah}:{ayah}', colour=0x467f05)
                em.set_author(name=f'{tafsirName}', icon_url=icon)
                fields = textwrap.wrap(entry, 1024, break_long_words=False)
                for _, item in enumerate(fields, 0):
                    em.add_field(name='\u200b', value=item, inline=False)
                await ctx.send(embed=em)


        elif tafsir == 'jalalayn':

            r = requests.get('https://raw.githubusercontent.com/galacticwarrior9/islambot/master/tafsir_jalalayn.txt')
            tafsir = r.text

            try:
                char1 = f'[{surah}:{ayah}]'
                endVerse = int(ayah) + 1
                char2 = f'[{surah}:{endVerse}]'

                text = tafsir[(tafsir.index(char1) + len(char1)):tafsir.index(char2)]
                text = u"{}".format(text).replace('`', '\\`').replace('(s)', '(ﷺ)').rstrip()

            except:
                char1 = f'[{surah}:{ayah}]'
                endSurah = int(surah) + 1
                char2 = f'[{endSurah}:1]'

                text = tafsir[(tafsir.index(char1) + len(char1)):tafsir.index(char2)]
                text = u"{}".format(text).replace('`', '\\`').rstrip()

            objects = textwrap.wrap(text, 5990, break_long_words=False)
            for object in objects:
                em = discord.Embed(title=f'{surah}:{ayah}', colour=0x467f05)
                em.set_author(name=f'{tafsirName}', icon_url=icon)
                fields = textwrap.wrap(object, 1024, break_long_words=False)
                for index, item in enumerate(fields, 0):
                    em.add_field(name='\u200b', value=item, inline=True)
                await ctx.send(embed=em)

        elif tafsir == 'tustari' or tafsir == 'kashani' or tafsir == 'kashf' or tafsir == 'wahidi' or tafsir == 'qushayri':
            fields = []

            t = EnglishTafsirSpecifics()

            surah, ayah = t.processRef(ref)

            tafsirName, tafsirID = t.getTafsirDetails(tafsir)

            formattedURL = t.makeURL(tafsirID, surah, ayah, page)

            content = str(await t.getTafsir(formattedURL))

            text = t.processText(content, tafsir)

            em = t.makeEmbed(text, page, tafsirName, surah, ayah)
            await ctx.send(embed=em)
            fields.clear()


class EnglishTafsirSpecifics:

    def __init__(self):
        self.baseurl = 'https://www.altafsir.com/Tafasir.asp?tMadhNo=0&tTafsirNo={}&tSoraNo={}&tAyahNo={}&tDisplay=yes&Page={}&Size=1&LanguageId=2'

    def makeURL(self, tafsirID, surah, ayah, page):
        url = self.baseurl.format(tafsirID, surah, ayah, page)
        return url

    async def getTafsir(self, formattedURL: str):
        async with ClientSession() as session:
            async with session.get(formattedURL) as response:
                return await response.text(encoding='cp1256')

    def processRef(self, ref: str):
        surah, ayah = ref.split(':')
        return surah, ayah

    def getTafsirDetails(self, tafsir):
        tafsirName = dictName[tafsir.lower()]
        tafsirID = dictID[tafsir.lower()]
        return tafsirName, tafsirID

    def makeEmbed(self, text, page, tafsirName, surah, ayah):
        if text is not None and text is not '' and text is not ' ':

            em = discord.Embed(title=f'Page {page}', colour=0x467f05)

            fields = textwrap.wrap(text, 1024, break_long_words = False)
            for x in fields:
                em.add_field(name='\u200b', value = x, inline = True)

            em.set_author(name=f'{tafsirName} | {surah}:{ayah}', icon_url=icon)

            if tafsirName == 'Asbāb al-Nuzūl':
                em.set_footer(text='Al-Wahidi includes dubious narrations in this work. Please be cautious.')

            return em

    def processText(self, content, tafsir):
        content = content.encode('cp1256').decode('cp1256')

        soup = BeautifulSoup(content, 'html.parser')
        for tag in soup.findAll('font',attrs={'class':'TextResultEnglish'}):
                tags.append(f' {tag.getText()}')
        for tag in soup.findAll('font',attrs={'class':'TextArabic'}):
                tags.append(tag.getText())

        text = ''.join(tags)
        tags.clear()

        return text

# Register as cog
def setup(bot):
    bot.add_cog(TafsirEnglish(bot))