import re
import discord
from helpers import prefix, get_site_source
from discord.ext import commands
from aiohttp import ClientSession
import textwrap

HADITH_BOOK_LIST = ['bukhari', 'muslim', 'tirmidhi', 'abudawud', 'nasai',
        'ibnmajah', 'malik', 'riyadussaliheen', 'adab', 'bulugh', 'qudsi',
        'nawawi', 'shamail']

ICON = 'https://sunnah.com/images/hadith_icon2_huge.png'

ERROR = 'The hadith could not be found on sunnah.com.'

INVALID_INPUT = f'Invalid arguments! Please do `{prefix}hadith (book name)' \
        f'[(book number):(hadith number)|(raw hadith number)]` \n' \
        f'Valid book names are `{HADITH_BOOK_LIST}`'

URL_FORMAT = "https://sunnah.com/{}/{}"


class HadithGrading:
    def __init__(self):
        self.narrator = None
        self.grading = None
        self.arabicGrading = None

        self.book_number = None
        self.hadith_number = None

        self.hadithText = None
        self.arabic_chapter_name = None
        self.chapter_name = None
        self.kitabName = None


class HadithSpecifics:
    def __init__(self, book_name, session, isEng, ref):
        self.session = session
        self.book_name = book_name.lower()
        self.url = URL_FORMAT

        self.raw_text = None
        self.embedTitle = None
        self.readableBookName = None
        self.hadith = HadithGrading()

        if isEng:
            self.hadithTextCSSClass = "text_details"
            self.formatBookName = self.formatEnglishBookName

            if ':' in ref:
                self.embedAuthorName = \
                        '{readableBookName} {book_number}:{hadith_number} ' \
                        '- {kitabName}'
            else:
                self.embedAuthorName = \
                        '{readableBookName}, Hadith {hadith_number}'

        else:
            self.hadithTextCSSClass = "arabic_hadith_full arabic"
            self.formatBookName = self.formatArabicBookName
            self.embedTitle = self.hadith.arabic_chapter_name

            if not self.isQudsiNawawi():
                self.embedAuthorName = \
                        '{readableBookName}'
            else:
                self.embedAuthorName = \
                        '{hadith_number} {readableBookName} , حديث'
        self.processRef(ref)

    def processRef(self, ref):
        if ':' in ref:
            (self.hadith.book_number,
                    self.hadith.hadith_number) = ref.split(":")
            self.url = self.url.format(self.book_name,
                    self.hadith.book_number) + f'/{self.hadith.hadith_number}'
        else:
            self.hadith.hadith_number = ref
            if self.isQudsiNawawi():
                self.book_name = self.book_name + '40'
            self.url = self.url.format(self.book_name,
                    self.hadith.hadith_number)

    async def getHadith(self, isEng = False, depth = 0):

        scanner = await get_site_source(self.url)

        for hadith in scanner.findAll("div",
                {"class": self.hadithTextCSSClass}, limit = 1):
            self.raw_text = hadith.text

        if (self.raw_text is None or self.raw_text == "None") and depth < 1:
            self.url = URL_FORMAT.format("urn", self.hadith.hadith_number)
            
            if isEng == True:
                await self.getHadith(isEng = True, depth = 1)
            else:
                await self.getHadith(isEng = False, depth = 1)

            return

        self.hadith.hadithText = self.formatHadithText(self.raw_text)

        for hadith in scanner.findAll("div",
                {"class": "hadith_narrated"}, limit = 1):
            self.hadith.narrator = hadith.text
            if isEng == True:
                self.embedTitle = self.hadith.narrator.replace('`','ʿ')

        if isEng == True:
            for hadith in scanner.findAll("td",
                    {"class": "english_grade"}, limit = 2):
                self.hadith.grading = hadith.text

        else:
            for hadith in scanner.findAll("td",
                    {"class": "arabic_grade arabic"}, limit = 1):
                self.hadith.arabicGrading = hadith.text.replace(')', '').replace('(', '')

        for hadith in scanner.findAll("div",
                {"class": "arabicchapter arabic"}, limit = 2):
            self.hadith.arabic_chapter_name = hadith.text
            if isEng == False:
                self.embedTitle = self.hadith.arabic_chapter_name

        for hadith in scanner.findAll("div",
                {"class": "book_page_english_name"}, limit = 1):
            self.hadith.kitabName = hadith.text.strip()

        self.readableBookName = self.formatBookName(self.book_name)

    def makeEmbed(self):
        authorName = self.embedAuthorName \
                .format(readableBookName = self.readableBookName,
                        book_number = self.hadith.book_number,
                        hadith_number = self.hadith.hadith_number,
                        kitabName = self.hadith.kitabName)

        em = discord.Embed(title = self.embedTitle, colour = 0x467f05)
        em.set_author(name = authorName, icon_url = ICON)

        list = textwrap.wrap(self.hadith.hadithText, 1024)
        for x in list:
            em.add_field(name="\u200b", value = x, inline = False)

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
                'shamail'        : "Shamā'il Muhammadiyyah",
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
                'shamail'        : 'الشمائل المحمدية',
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
        await self.abstract_hadith(ctx, book_name, ref, isEng = True)

    @commands.command(name='ahadith')
    async def ahadith(self, ctx, book_name: str = None, ref: str = None):
        await self.abstract_hadith(ctx, book_name, ref)

    async def abstract_hadith(self, ctx, book_name, ref, isEng = False):
        if book_name in HADITH_BOOK_LIST:
            spec = HadithSpecifics(book_name, self.session, isEng, ref)
        else:
            await ctx.send(INVALID_INPUT)
            return
        if isEng == True:
            await spec.getHadith(isEng = True)
        else:
            await spec.getHadith(isEng = False)

        if spec.hadith.hadithText is not None \
                and spec.hadith.hadithText != "None":
            em = spec.makeEmbed()
            await ctx.send(embed=em)
        else:
            await ctx.send(ERROR)

    async def abstract_hadith_from_link(self, message, book_name, ref, isEng = True):

        if book_name in HADITH_BOOK_LIST:
            spec = HadithSpecifics(book_name, self.session, isEng, ref)
        else:
            return

        await spec.getHadith(isEng = True)

        if spec.hadith.hadithText is not None \
                and spec.hadith.hadithText != "None":
            em = spec.makeEmbed()
            return em

    def findURL(self, message):
        urls = re.findall(r'(https?://\S+)', message)
        for link in urls:
            if "sunnah.com/" in link:
                return link

    @commands.Cog.listener()
    async def on_message(self, message):
        content = message.content
        url = self.findURL(content)
        if url is not None:
            try:
                meta = url.split("/")
                name = meta[3]
                book = meta[4]
                hadith = meta[5]
                ref = f"{book}:{hadith}"
                em = await self.abstract_hadith_from_link(message, name, ref, True)
                await message.channel.send(embed=em)

            except:
                return

# Register as cog
def setup(bot):
    bot.add_cog(Hadith(bot))
