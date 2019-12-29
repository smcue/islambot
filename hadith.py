import re
import discord
from helpers import prefix
from bs4 import BeautifulSoup
from discord.ext import commands
from aiohttp import ClientSession
import textwrap

hadith_book_list = ['bukhari', 'muslim', 'tirmidhi', 'abudawud', 'nasai', 'ibnmajah', 'malik', 'riyadussaliheen',
                    'adab', 'bulugh', 'qudsi', 'nawawi']

icon = 'https://sunnah.com/images/hadith_icon2_huge.png'
error = ('The hadith could not be found on sunnah.com. This could be because it does not exist, '
         'or due to the irregular structure of the website.')


class HadithGrading:
    def __init__(self):
        self.narrator = None
        self.grading = None
        self.arabicGrading = None

        self.book_number = None
        self.hadith_number = None

        self.hadithText = None
        self.chapter_name = None
        self.kitabName = None


class HadithSpecifics:
    def __init__(self, book_name, session, isEng):
        self.session = session
        self.book_name = book_name.lower()
        self.url = 'https://sunnah.com/{}/{}'

        self.raw_text = None
        self.readableBookName = None
        self.hadith = HadithGrading()

        if isEng:
            self.hadithTextCSSClass = "text_details"
            self.formatBookName = self.formatEnglishBookName

            if not self.isQudsiNawawi():
                self.embedAuthorName = '{readableBookName} {book_number}:{hadith_number} - {kitabName}'
            else:
                self.embedAuthorName = '{readableBookName}, Hadith {hadith_number}'

        else:
            self.hadithTextCSSClass = "arabic_hadith_full arabic"
            self.formatBookName = self.formatArabicBookName
            self.embedTitle = self.hadith.chapter_name

            if not self.isQudsiNawawi():
                self.embedAuthorName = '{book_number}:{hadith_number} - {readableBookName}'
            else:
                self.embedAuthorName = '{hadith_number} {readableBookName} , حديث'

    def processRef(self, ref):
        if not self.isQudsiNawawi():
            self.hadith.book_number, self.hadith.hadith_number = ref.split(":")
            self.url = self.url.format(self.book_name, self.hadith.book_number) + f'/{self.hadith.hadith_number}'

        else:
            self.hadith.hadith_number = ref
            self.book_name = self.book_name + '40'
            self.url = self.url.format(self.book_name, self.hadith.hadith_number)

    async def getHadith(self):
        async with self.session.get(self.url) as resp:
            data = await resp.read()
        scanner = BeautifulSoup(data, "html.parser")

        for hadith in scanner.findAll("div", {"class": self.hadithTextCSSClass}):
            self.raw_text = hadith.text

        self.hadith.hadithText = self.formatHadithText(self.raw_text)

        for hadith in scanner.findAll("div", {"class": "hadith_narrated"}):
            self.hadith.narrator = hadith.text
            self.embedTitle = self.hadith.narrator

        for hadith in scanner.findAll("td", {"class": "english_grade"}):
            self.hadith.grading = hadith.text

        for hadith in scanner.findAll("td", {"class": "arabic_grade arabic"}):
            self.hadith.arabicGrading = hadith.text

        for hadith in scanner.findAll("div", {"class": "arabicchapter arabic"}):
            self.hadith.arabic_chapter_name = hadith.text

        for hadith in scanner.findAll("div", {"class": "book_page_english_name"}):
            self.hadith.kitabName = hadith.text.strip()

        self.readableBookName = self.formatBookName(self.book_name)

    def makeEmbed(self):


        authorName = self.embedAuthorName.format(readableBookName = self.readableBookName,
                                                 book_number = self.hadith.book_number,
                                                 hadith_number = self.hadith.hadith_number,
                                                 kitabName = self.hadith.kitabName)

        em = discord.Embed(title = self.embedTitle, colour = 0x467f05)
        em.set_author(name = authorName, icon_url = icon)

        list = textwrap.wrap(self.hadith.hadithText, 1024)
        for x in list:
            em.add_field(name="\a", value = x, inline = False)

        if self.hadith.grading:
           em.set_footer(text = f'Grading{self.hadith.grading}')

        if self.hadith.arabicGrading:
            em.set_footer(text = f'{self.hadith.arabicGrading}')


        return em

    @staticmethod
    def formatHadithText(text):
        txt = str(text) \
            .replace('`', 'ʿ') \
            .replace('\n', '') \
            .replace('<i>', '*') \
            .replace('</i>', '*') \

        return re.sub('\s+', ' ', txt)

    @staticmethod
    def formatEnglishBookName(book_name):
        bookDict = {
            'bukhari'        : 'Sahīh al-Bukhārī',
            'muslim'         : 'Sahīh Muslim',
            'tirmidhi'       : 'Jamiʿ at-Tirmidhī',
            'abudawud'       : 'Sunan Abī Dāwūd',
            'nasai'          : "Sunan an-Nāsaʿī",
            'ibnmajah'       : 'Sunan Ibn Mājah',
            'malik'          : 'Muwatta Mālik',
            'riyadussaliheen': 'Riyadh as-Salihīn',
            'adab'           : "Al-Adab al-Mufrad",
            'bulugh'         : 'Bulugh al-Maram',
            'qudsi40'        : 'Al-Arbaʿīn al-Qudsiyyah',
            'nawawi40'       : 'Al-Arbaʿīn al-Nawawiyyah'
        }

        return bookDict[book_name]

    @staticmethod
    def formatArabicBookName(book_name):
        bookDict = {
            'bukhari'        : 'صحيح البخاري',
            'muslim'         : 'صحيح مسلم',
            'tirmidhi'       : 'جامع الترمذي',
            'abudawud'       : 'سنن أبي داود',
            'nasai'          : "سنن النسائي",
            'ibnmajah'       : 'سنن ابن ماجه',
            'malik'          : 'موطأ مالك',
            'riyadussaliheen': 'رياض الصالحين',
            'adab'           : "الأدب المفرد",
            'bulugh'         : 'بلوغ المرام',
            'qudsi40'        : 'الأربعون القدسية',
            'nawawi40'       : 'الأربعون النووية'
        }

        return bookDict[book_name]

    def isQudsiNawawi(self):
        return self.book_name in ['qudsi', 'nawawi', 'qudsi40', 'nawawi40']


class Hadith(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = ClientSession(loop = bot.loop)

    @commands.command(name='hadith')
    async def hadith(self, ctx, book_name: str = None, ref: str = None):

        if book_name in hadith_book_list:
            spec = self.getSpec(book_name, ref, self.session, isEng = True)
        else:
            await ctx.send(f'Invalid arguments! '
                               f'Please do `{prefix}hadith (book name) (book number):(hadith number)` \n'
                               f'Valid book names are `{hadith_book_list}`')
            return
        await spec.getHadith()

        if spec.hadith.hadithText is not None and spec.hadith.hadithText != "None":
            em = spec.makeEmbed()
            await ctx.send(embed=em)

        else:
            await ctx.send(error)

    @commands.command(name='ahadith')
    async def ahadith(self, ctx, book_name: str, ref: str = None):

        if book_name in hadith_book_list:
            spec = self.getSpec(book_name, ref, self.session)
        else:
            await ctx.send(f'Invalid arguments! '
                               f'Please do `{prefix}hadith (book name) (book number):(hadith number)` \n'
                               f'Valid book names are `{hadith_book_list}`')
            return

        await spec.getHadith()

        if spec.hadith.hadithText is not None:
            em = spec.makeEmbed()
            await ctx.send(embed=em)
        else:
            await ctx.send(error)

    @staticmethod
    def getSpec(book_name, ref, session, isEng = False):
        spec = HadithSpecifics(book_name, session, isEng)
        spec.processRef(ref)
        return spec


# Register as cog
def setup(bot):
    bot.add_cog(Hadith(bot))
