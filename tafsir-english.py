from discord.ext import commands
import discord
import textwrap
from helpers import get_site_source

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

invalid_verse = '**Invalid verse.** Please type the command in this format: `-tafsir surah:ayah tafsirname`.' \
                '\n\ne.g. `-tafsir 1:1 ibnkathir`'

invalid_tafsir = "**Couldn't find tafsir!** Please choose from the following: `ibnkathir`, `jalalayn`, `qushayri`, " \
                 "`wahidi`, `tustari`, `kashf`."


class TafsirEnglish(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.baseurl = 'https://www.altafsir.com/Tafasir.asp?tMadhNo=0&tTafsirNo={}&tSoraNo={}&tAyahNo={}&tDisplay=y' \
                       'es&Page={}&Size=1&LanguageId=2'

    @commands.command(name='tafsir')
    async def tafsir(self, ctx, ref: str, tafsir: str = "jalalayn", page: str = 1):

        try:
            surah, ayah = ref.split(':')
        except:
            return await ctx.send(invalid_verse)

        try:
            tafsirName = dictName[tafsir.lower()]
        except:
           return await ctx.send(invalid_tafsir)

        if tafsir == 'ibnkathir':

            soup = await get_site_source(f'http://www.alim.org/library/quran/AlQuran-tafsir/TIK/{surah}/{ayah}')

            text = self.processText(soup, tafsir)
            text = self.format_text(text)

            # Paginate results:
            pages = textwrap.wrap(text, 2048, break_long_words=False)
            num_pages = len(pages)

            # We only want to send the first page:
            try:
                text = pages[0]
            except IndexError:
                return await ctx.send("Sorry, there is no tafsir available for this verse. Try using Tafsir al-Jalala"
                                      f"yn (`-tafsir {surah}:{ayah} jalalayn`).")

            text = text.replace('#', '\n')
            em = self.makeEmbed(text, tafsirName, surah, ayah, page)
            msg = await ctx.send(embed=em)

            if num_pages > 1:
                await msg.add_reaction(emoji='➡')

        elif tafsir == 'jalalayn':

            rawText = await get_site_source('https://raw.githubusercontent.com/galacticwarrior9/islambot/master/tafsir_jalalayn.txt')
            rawText = rawText.decode('utf-8')

            try:
                char1 = f'[{surah}:{ayah}]'
                endVerse = int(ayah) + 1
                char2 = f'[{surah}:{endVerse}]'

                text = rawText[(rawText.index(char1) + len(char1)):rawText.index(char2)]
                text = u"{}".format(text).replace('`', '\\`').replace('(s)', '(ﷺ)').rstrip()

            except:
                char1 = f'[{surah}:{ayah}]'
                endSurah = int(surah) + 1
                char2 = f'[{endSurah}:1]'

                text = rawText[(rawText.index(char1) + len(char1)):rawText.index(char2)]
                text = u"{}".format(text).replace('`', '\\`').rstrip()

            em = self.makeEmbed(text, tafsirName, surah, ayah, page)
            await ctx.send(embed=em)

        elif tafsir == 'tustari' or tafsir == 'kashani' or tafsir == 'kashf' or tafsir == 'wahidi' or tafsir == 'qushayri':

            surah, ayah = self.processRef(ref)
            tafsirName, tafsirID = self.getTafsirDetails(tafsir)
            formattedURL = self.makeURL(self, tafsirID, surah, ayah, page)
            rawText = await get_site_source(formattedURL)
            text = self.processText(rawText, tafsir)

            em = self.makeEmbed(text, tafsirName, surah, ayah, page)
            await ctx.send(embed=em)

    @staticmethod
    def makeURL(self, tafsirID, surah, ayah, page):
        url = self.baseurl.format(tafsirID, surah, ayah, page)
        return url

    @staticmethod
    def processRef(ref: str):
        surah, ayah = ref.split(':')
        return surah, ayah

    @staticmethod
    def getTafsirDetails(tafsir):
        tafsirName = dictName[tafsir.lower()]
        tafsirID = dictID[tafsir.lower()]
        return tafsirName, tafsirID

    @staticmethod
    def makeEmbed(text, tafsir, surah, ayah, page):
        if len(text) > 2048:
            text = text[:2046] + '...'
        em = discord.Embed(title=f'{surah}:{ayah}', colour=0x467f05, description=text)
        em.set_author(name=f'{tafsir}', icon_url=icon)
        if tafsir == 'Tafsīr Ibn Kathīr':
            em.set_footer(text=f"Page {page}")
        return em

    @staticmethod
    def processText(content, tafsir):
        tags = []

        if tafsir == 'ibnkathir':
            p_tags = content.find_all('p')
            x = 0
            for tag in range(len(p_tags)):
                tags.append(p_tags[x].get_text())
                x += 1

        else:
            for tag in content.findAll('font', attrs={'class': 'TextResultEnglish'}):
                tags.append(f' {tag.getText()}')
            for tag in content.findAll('font', attrs={'class': 'TextArabic'}):
                tags.append(tag.getText())

        text = ''.join(tags)

        return text

    @staticmethod
    def format_text(text):
        text = text.replace("Thanks for visiting Alim.org, The Alim Foundation's flagship site that provides the w"
                            "orld's only social network built around Qur'an, Hadith, and other classical sources of"
                            " Islamic knowledge.", '') \
            .replace("We are a free service run by many volunteers and we need your help to stay that way. Please"
                     " consider a small donation(tax-deductible in the USA) to help us improve Alim.org by adding"
                     " more content and getting faster servers.", '') \
            .replace("Share your thoughts about this with others by posting a comment.  "
                     "Visit our FAQ for some ideas.", '') \
            .replace('`', 'ʿ') \
            .replace('﴾', '##') \
            .replace('﴿', '##') \
            .replace('»', '»##') \
            .replace('«', ' ##«') \
            .replace('bin', 'b. ') \
            .replace('Hadith', 'hadith') \
            .replace('No Comments', '') \
            .replace('Messenger of Allah', 'Messenger of Allah ﷺ') \
            .replace(' )', ')')

        return text

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.message.author == self.bot.user and user != self.bot.user:

            embed = reaction.message.embeds[0]
            surah, ayah = self.processRef(embed.title)
            tafsir = 'Tafsīr Ibn Kathīr'
            page = int(embed.footer.text.split()[1])

            soup = await get_site_source(f'http://www.alim.org/library/quran/AlQuran-tafsir/TIK/{surah}/{ayah}')

            text = self.processText(soup, 'ibnkathir')
            text = self.format_text(text)

            pages = textwrap.wrap(text, 2048, break_long_words=False)
            num_pages = len(pages)

            if reaction.emoji == '➡':
                await reaction.message.remove_reaction(emoji="➡", member=user)
                new_page = page + 1
                if new_page <= num_pages:
                    text = pages[new_page - 1]
                    text = text.replace('#', '\n')
                    em = self.makeEmbed(text, tafsir, surah, ayah, new_page)
                    await reaction.message.edit(embed=em)
                    await reaction.message.add_reaction(emoji='⬅')
                    if new_page == num_pages:
                        await reaction.message.remove_reaction(emoji="➡", member=self.bot.user)

            if reaction.emoji == '⬅':
                await reaction.message.remove_reaction(emoji="⬅", member=user)
                new_page = page - 1
                if new_page > 0:
                    text = pages[new_page - 1]
                    text = text.replace('#', '\n')
                    em = self.makeEmbed(text, tafsir, surah, ayah, new_page)
                    await reaction.message.edit(embed=em)
                    await reaction.message.add_reaction(emoji='➡')
                    if new_page == 1:
                        await reaction.message.remove_reaction(emoji='⬅', member=self.bot.user)


# Register as cog
def setup(bot):
    bot.add_cog(TafsirEnglish(bot))
