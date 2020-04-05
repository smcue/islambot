import textwrap
from discord.ext import commands
from bs4 import BeautifulSoup
import discord
from aiohttp import ClientSession

icon = 'https://lh5.ggpht.com/lRz25mOFrRL42NuHtuSCneXbWV2Gtm7iYZ5eQbuA7JWUC3guWaTaQxNJ7j9rsRMCNAU=w150'

dictName = {
    'maturidi': 'تأويلات أهل السنة / الماتريدي',
    'tabari': 'جامع البيان في تفسير القرآن / الطبري',
    'ibnashur': 'التحرير والتنوير / ابن عاشور',
    'qurtubi': 'الجامع لاحكام القرآن / القرطبي',
    'mawardi': 'النكت والعيون / الماوردي',
    'baghawi': 'معالم التنزيل / البغوي',
    'nasafi': 'مدارك التنزيل وحقائق التأويل / النسفي',
    'ibnabdalsalam': 'تفسير القرآن / ابن عبد السلام',
    "sa'di": 'تيسير الكريم الرحمن في تفسير كلام المنان / عبد الرحمن بن ناصر بن السعدي',
    'hashiyajalalayn': 'حاشية الصاوي / تفسير الجلالين',
    'samarqandi': 'بحر العلوم / السمرقندي',
    'razi': 'مفاتيح الغيب ، التفسير الكبير/ الرازي',
    'ibnkathir': 'تفسير القرآن العظيم/ ابن كثير',
    'shawkani': 'فتح القدير/ الشوكاني',
    'ibnaljawzi': 'زاد المسير في علم التفسير/ ابن الجوزي',
    'duralmanthur': 'الدر المنثور في التفسير بالمأثور/ السيوطي',
    'zamakhshari': 'الكشاف / الزمخشري',
    'baydawi': 'انوار التنزيل واسرار التأويل / البيضاوي',
    'jalalayn': 'تفسير الجلالين / المحلي و السيوطي',
    'jilani': 'تفسير الجيلاني / الجيلاني',
    'ibnattiyah': 'المحرر الوجيز في تفسير الكتاب العزيز / ابن عطية',
    "tha'labi": 'الكشف والبيان / الثعلبي',
    'ibnjuzayy': 'التسهيل لعلوم التنزيل / ابن جزي الغرناطي',
    'khazin': 'لباب التأويل في معاني التنزيل / الخازن',
    'abuhayyan': 'البحر المحيط / ابو حيان',
    "baqa'i": 'نظم الدرر في تناسب الآيات والسور / البقاعي',
    'tustari': 'تفسير القرآن/ التستري مصنف و مدقق',
    'salami': 'تفسير حقائق التفسير/ السلمي مصنف و مدقق',
    'qushayri': 'تفسير لطائف الإشارات / القشيري'
}

dictBuggedNames = {
    'maturidi': 'تفسير تأويلات أهل السنة/ الماتريدي  (ت 333هـ)',
    'tabari': 'تفسير جامع البيان في تفسير القرآن/ الطبري (ت 310 هـ)',
    'ibnashur': 'تفسير التحرير والتنوير/ ابن عاشور (ت 1393 هـ)',
    'qurtubi': 'تفسير الجامع لاحكام القرآن/ القرطبي (ت 671 هـ)',
    'mawardi': 'تفسير النكت والعيون/ الماوردي (ت 450 هـ)',
    'baghawi': 'تفسير معالم التنزيل/ البغوي (ت 516 هـ)',
    'nasafi': 'تفسير مدارك التنزيل وحقائق التأويل/ النسفي (ت 710 هـ)',
    'ibnabdalsalam': 'تفسير القرآن/ ابن عبد السلام (ت 660 هـ)',
    "sa'di": 'تفسير تيسير الكريم الرحمن في تفسير كلام المنان/ عبد الرحمن بن ناصر بن السعدي (ت 1376هـ)',
    'hashiyajalalayn': 'تفسير حاشية الصاوي / تفسير الجلالين(ت1241هـ)',
    'samarqandi': 'تفسير بحر العلوم/ السمرقندي (ت 375 هـ)',
    'razi': 'تفسير مفاتيح الغيب ، التفسير الكبير/ الرازي (ت 606 هـ)',
    'ibnkathir': 'تفسير تفسير القرآن العظيم/ ابن كثير (ت 774 هـ)',
    'shawkani': 'تفسير فتح القدير/ الشوكاني (ت 1250 هـ)',
    'ibnaljawzi': 'تفسير زاد المسير في علم التفسير/ ابن الجوزي (ت 597 هـ)',
    'duralmanthur': 'تفسير الدر المنثور في التفسير بالمأثور/ السيوطي (ت 911 هـ)',
    'zamakhshari': 'تفسير الكشاف/ الزمخشري (ت 538 هـ)',
    'baydawi': 'تفسير انوار التنزيل واسرار التأويل/ البيضاوي (ت 685 هـ)',
    'jalalayn': 'تفسير تفسير الجلالين/ المحلي و السيوطي (ت المحلي 864 هـ)',
    'jilani': 'تفسير تفسير الجيلاني/ الجيلاني (ت713هـ)',
    'ibnattiyah': 'تفسير المحرر الوجيز في تفسير الكتاب العزيز/ ابن عطية (ت 546 هـ)',
    "tha'labi": 'تفسير الكشف والبيان / الثعلبي (ت 427 هـ)',
    'ibnjuzayy': 'تفسير التسهيل لعلوم التنزيل / ابن جزي الغرناطي (ت 741 هـ)',
    'khazin': 'تفسير لباب التأويل في معاني التنزيل/ الخازن (ت 725 هـ)',
    'abuhayyan': 'تفسير البحر المحيط/ ابو حيان (ت 754 هـ)',
    "baqa'i": 'تفسير نظم الدرر في تناسب الآيات والسور/ البقاعي (ت 885 هـ)',
    'tustari': 'تفسير القرآن/ التستري (ت 283 هـ)',
    'salami': 'تفسير حقائق التفسير/ السلمي (ت 412 هـ)',
    'qushayri': 'تفسير لطائف الإشارات / القشيري (ت 465 هـ)'
}

dictID = {
    'maturidi': 94,
    'tabari': 1,
    'ibnashur': 54,
    'qurtubi': 5,
    'mawardi': 12,
    'baghawi': 13,
    'nasafi': 17,
    'ibnabdalsalam': 16,
    "sa'di": 98,
    'hashiyajalalayn': 96,
    'samarqandi': 11,
    'razi': 4,
    'ibnkathir': 7,
    'shawkani': 9,
    'ibnaljawzi': 15,
    'duralmanthur': 26,
    'zamakhshari': 2,
    'baydawi': 6,
    'jalalayn': 8,
    'jilani': 95,
    'ibnattiyah': 14,
    "tha'labi": 75,
    'ibnjuzayy': 88,
    'khazin': 18,
    'abuhayyan': 19,
    "baqa'i": 25,
    'tustari': 29,
    'salami': 30,
    'qushayri': 31,
}


class TafsirSpecifics:

    def __init__(self):
        self.baseurl = 'https://www.altafsir.com/Tafasir.asp?tMadhNo=0&tTafsirNo={}&tSoraNo={}&tAyahNo={}&tDisplay=' \
                       'yes&Page={}&Size=1&LanguageId=1'

    def makeURL(self, tafsirID, surah, ayah, page):
        url = self.baseurl.format(tafsirID, surah, ayah, page)
        return url

    async def getTafsir(self, formattedURL: str):
        async with ClientSession() as session:
            async with session.get(formattedURL) as response:
                return await response.text(encoding='cp1256')

    def getTafsirID(self, tafsir):
        tafsirName = dictName[tafsir.lower()]
        tafsirID = dictID[tafsir.lower()]
        return tafsirName, tafsirID

    def getTafsirIDFromArabic(self, arabicName):
        for englishName, value in dictName.items():
            if value == arabicName:
                _, tafsirID = TafsirSpecifics.getTafsirID(self, englishName)
                return tafsirID, englishName

    def processRef(self, ref: str):
        surah, ayah = ref.split(':')
        return surah, ayah

    def makeEmbed(self, text, page, tafsirName, surah, ayah):
        if text is not None and text is not '' and text is not ' ':

            em = discord.Embed(title=f'Page {page}', colour=0x467f05)

            fields = textwrap.wrap(text, 1024, break_long_words = False)
            for x in fields:
                em.add_field(name = '\u200b', value = x, inline = False)

            tafsirName = tafsirName.replace('(', ' -  ') \
                .replace(')', '')

            em.set_author(name=f'{tafsirName} | {surah}:{ayah}', icon_url=icon)

            return em

    def processText(self, content, tafsir):
        content = content.encode('cp1256').decode('cp1256')

        '''
        We want to edit the page so the ayah references show up.
        Firstly, we delete the ayah overview at the beginning of each page.
        Then we delete the tags surrounding the ayat so they are detected by the bot.
        '''

        content = str(content) \
            .replace('<font class="TextAyah" id="AyahText">', ' ') \
            .replace('<font class="TextAyah"', '  ')

        soup = BeautifulSoup(content, 'html.parser')

        tags = []

        for tag in soup.findAll('font', attrs={'class': 'TextResultArabic'}):
            tags.append(f' {tag.getText()}')  # For each tag with Arabic text, add it to a list.

        text = ''.join(tags)  # Convert the list into a string.

        text = text.replace('ويسعدنا استقبال اقتراحاتكم وملاحظاتكم عبر البريد الإلكتروني المخصص ', '') \
            .replace("هل تؤيد تغيير مخطط وتصميم الموقع ليواكب التطورات التكنولوجية؟ زوارنا الكرام، نشكركم على إبداء رأيكم لمساعدتنا في اتخاذ القرار المناسب والمرضي لكم بناء على نتائج التصويت.", '') \
            .replace('(altafsir@itgsolutions.com)', '') \
            .replace('مصنف', '') \
            .replace('و مدقق', '') \
            .replace('مرحلة اولى', '') \
            .replace('*', '') \
            .replace(dictBuggedNames[tafsir], '') \
            .replace('\r\n\r\n\n', '') \
            .replace('  ', '') \
            .replace("و لم يتم تدقيقه بعد", '')

        text = "\n".join([ll.rstrip() for ll in text.splitlines() if ll.strip()])  # Delete blank lines

        return text


class Tafsir(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="atafsir")
    async def atafsir(self, ctx, ref: str, tafsir: str = "tabari", page : int = 1):

        t = TafsirSpecifics()

        surah, ayah = t.processRef(ref)

        tafsirName, tafsirID = t.getTafsirID(tafsir)

        formattedURL = t.makeURL(tafsirID, surah, ayah, page)

        content = str(await t.getTafsir(formattedURL))

        text = t.processText(content, tafsir)

        em = t.makeEmbed(text, page, tafsirName, surah, ayah)

        msg = await ctx.send(embed=em)
        await msg.add_reaction(emoji="⬅")
        await msg.add_reaction(emoji='➡')

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        t = TafsirSpecifics()
        if reaction.message.author.id == 352815253828141056 and user.id != 352815253828141056:
            embed = reaction.message.embeds[0]

            arabicName = embed.author.name.split('|', 1)[0][:-1]  # Delete last character as it's blank.

            ref = embed.author.name.split('|', 1)[1].strip()
            surah, ayah = t.processRef(ref)
            page = int(embed.title.split()[1])
            tafsirID, tafsir = t.getTafsirIDFromArabic(arabicName)

            if reaction.emoji == '➡':
                newPage = int(embed.title.split()[1]) + 1
                formattedURL = t.makeURL(tafsirID, surah, ayah, newPage)
                content = str(await t.getTafsir(formattedURL))

                text = t.processText(content, tafsir)

                em = t.makeEmbed(text, newPage, arabicName, surah, ayah)
                if em is not None:
                    await reaction.message.edit(embed=em)

            elif reaction.emoji == '⬅':
                if page > 1:
                    newPage = int(embed.title.split()[1]) - 1
                    formattedURL = t.makeURL(tafsirID, surah, ayah, newPage)
                    content = str(await t.getTafsir(formattedURL))

                    text = t.processText(content, tafsir)

                    em = t.makeEmbed(text, newPage, arabicName, surah, ayah)
                    if em is not None:
                        await reaction.message.edit(embed=em)


# Register as cog
def setup(bot):
    bot.add_cog(Tafsir(bot))
