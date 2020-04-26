import re
import mysql.connector
import aiohttp
from discord.ext import commands
from discord.ext.commands import has_permissions
from utils import makeEmbed
from helpers import processRef, Specifics, prefix, convertToArabicNumber

INVALID_TRANSLATION = "**Invalid translation**. List of translations: <https://github.com/galacticwarrior9/is" \
                      "lambot/blob/master/Translations.md>"

INVALID_ARGUMENTS_ARABIC = "Invalid arguments! Do `{0}aquran [surah]:[ayah]`. Example: `{0}aquran 1:1`" \
                               "\nTo fetch multiple verses, do `{0}quran [surah]:[first ayah]-[last ayah]`" \
                               "\nExample: `{0}aquran 1:1-7`".format(prefix)

INVALID_ARGUMENTS_ENGLISH = "Invalid arguments! Do `{0}aquran [surah]:[ayah]`. Example: `{0}aquran 1:1`" \
                               "\nTo fetch multiple verses, do `{0}quran [surah]:[first ayah]-[last ayah]`" \
                               "\nExample: `{0}aquran 1:1-7`".format(prefix)

SQL_ERROR = "There was an error connecting to the database."

icon = 'https://cdn6.aptoide.com/imgs/6/a/6/6a6336c9503e6bd4bdf98fda89381195_icon.png?w=256'


class QuranSpecifics(Specifics):
    def __init__(self, surah, minayah, maxayah, edition):
        super().__init__(surah, minayah, maxayah)
        self.edition = edition


class Quran(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=bot.loop)
        self.url1 = 'http://api.alquran.cloud/ayah/{}:{}/{}'
        self.url2 = 'http://api.quran.com:3000/api/v3/chapters/{}/verses?page=1&limit=1&offset={}&translations[]={}'
        self.mysqlDetails = open('mysql.txt').read().splitlines()
        self.host = self.mysqlDetails[0]
        self.user = self.mysqlDetails[1]
        self.password = self.mysqlDetails[2]
        self.database = self.mysqlDetails[3]

    @staticmethod
    def formatEdition(edition):
        editionDict = {
            'mammadaliyev': 'az.mammadaliyev',
            'musayev': 'az.musayev',
            'bengali': 'bn.bengali',
            'bulgarian': 'bg.theophanov',
            'bosnian': 25,
            'hrbek': 'cs.hrbek',
            'nykl': "cs.nykl",
            'aburida': 'de.aburida',
            'bubenheim': 'de.bubenheim',
            'khoury': 'de.khoury',
            'zaidan': "de.zaidan",
            'divehi': 'dv.divehi',
            'amharic': 87,
            'haleem': 85,
            'taqiusmani': 84,
            'khattab': 101,
            'ghali': 17,
            'finnish': 30,
            'indonesian': 33,
            'tajik': 74,
            'chechen': 106,
            'czech': 26,
            'sahih': 20,
            'ahmedali': 'en.ahmedali',
            'arberry': 'en.arberry',
            'asad': 'en.asad',
            'daryabadi': 'en.daryabadi',
            'hilali': 18,
            'pickthall': 19,
            'qaribullah': 'en.qaribullah',
            'sarwar': 'en.sarwar',
            'yusufali': 22,
            'shakir': 'en.shakir',
            'transliteration': 'en.transliteration',
            'spanish': 83,
            'ansarian': 'fa.ansarian',
            'ayati': 'fa.ayati',
            'fooladvand': 'fa.fooladvand',
            'ghomshei': 'fa.ghomshei',
            'makarem': 'fa.makarem',
            'french': 31,
            'hausa': 32,
            'hindi': 82,
            'italian': 34,
            'japanese': 'ja.japanese',
            'korean': 'ko.korean',
            'kurdish': 	81,
            'malayalam': 37,
            'dutch': 40,
            'norwegian': 'no.berg',
            'polish': 'pl.bielawskiego',
            'portuguese': 'pt.elhayek',
            'romanian': 'ro.grigore',
            'kuliev': 45,
            'osmanov': 'ru.osmanov',
            'porokhova': 'ru.porokhova',
            'sindhi': 'sd.amroti',
            'somali': 46,
            'ahmeti': 'sq.ahmeti',
            'mehdiu': 'sq.mehdiu',
            'nahi': 'sq.nahi',
            'swedish': 48,
            'swahili': 'sw.barwani',
            'tamil': 'ta.tamil',
            'thai': 'th.thai',
            'ates': 'tr.ates',
            'bulac': 'tr.bulac',
            'diyanet': 77,
            'golpinarli': 'tr.golpinarli',
            'ozturk': 'tr.ozturk',
            'vakfi': 'tr.vakfi',
            'yazir': 'tr.yazir',
            'yildirim': 'tr.yildirim',
            'yuksel': 'tr.yuksel',
            'tatar': 'tt.nugman',
            'uyghur': 'ug.saleh',
            'jalandhry': 'ur.jalandhry',
            'jawadi': 'ur.jawadi',
            'qadri': 'ur.qadri',
            'urdu': 97,
            'maududi': 97,
            'junagarhi': 54,
            'maududi.en': 95,
            'malay': 39,
            'uzbek': 'uz.sodik',
            'chinese': 'zh.jian',
            'ukrainian': 104,
            'abuadel': 79,
            'maranao': 38
        }
        return editionDict[edition]

    @staticmethod
    def getEditionName(edition):
        editionNames = {
            85: 'Abdel Haleem',
            101: "Dr. Mustafa Khattab",
            84: "Mufti Taqi Usmani",
            17: "Dr. Ghali",
            22: "Yusuf Ali",
            30: "Finnish",
            33: "Bahasa Indonesia (Kementerian Agama)",
            74: "Tajik (Abdolmohammad Ayati)",
            106: "Chechen (Magomed Magomedov)",
            87: "አማርኛ (Sadiq & Sani)",
            20: 'Sahih International',
            31: 'Français (Muhammad Hamidullah)',
            77: 'Türkçe (Diyanet İşleri)',
            81: 'Kurdî (Burhan Muhammad-Amin)',
            82: 'हिन्दी (Suhel Farooq Khan)',
            95: 'Abul Ala Maududi (with tafsir)',
            26: 'Čeština',
            104: 'Українська мова (Mykhaylo Yakubovych)',
            83: 'Español (Sheikh Isa García)',
            37: 'മലയാളം (Abdul Hameed & Kunhi Mohammed)',
            19: 'Pickthall',
            18: 'Muhsin Khan & Hilali',
            34: 'Italiano (Hamza Roberto Piccardo)',
            39: 'Bahasa Melayu (Abdullah Muhammad Basmeih)',
            97: 'اردو, (ابو الاعلی مودودی)',
            54: 'اردو, (محمد جوناگڑھی)',
            40: 'Nederlands (Salomo Keyzer)',
            25: 'Bosanski',
            45: 'Русский (Эльми́р Кули́ев)',
            79: 'Русский (Абу Адель)',
            78: 'Русский (Министерство вакуфов, Египта)',
            48: 'Svenska (Knut Bernström)',
            32: 'Hausa (Abubakar Mahmoud Gumi)',
            38: 'Mëranaw',
            46: 'Af-Soomaali (Mahmud Muhammad Abduh)'
        }
        return editionNames[edition]

    @staticmethod
    def getLanguageCode(edition):
        languageCodes = {
            31: 'fr',  # Hamidullah, French
            97: 'ur',  # Maududi, Urdu
            54: 'ur',  # Junagarhi, Urdu
            'ur.jalandhry': 'ur',
            'ur.jawadi': 'ur',
            'ur.qadri': 'ur',
            83: 'es',  # Isa Garcia, Spanish
            40: 'nl',  # Salomo Keyzar, Dutch
            25: 'bs',  # Bosnian
            33: 'id',  # Indonesian
            45: 'ru',  # Kuliev, Russian
            78: 'ru',  # Ministry of Awqaf, Russian
            79: 'ru',  # Abu Adel, Russian
            48: 'sv',  # Knut Bernström, Swedish
        }
        return languageCodes[edition]

    @staticmethod
    def isQuranCom(edition):
        if isinstance(edition, int):
            return True
        else:
            return False

    @commands.command(name="settranslation")
    @has_permissions(manage_guild=True)
    async def settranslation(self, ctx, translation: str):

        if translation is None:
            await ctx.send(INVALID_TRANSLATION)
            return

        try:
            self.formatEdition(translation)
            connection = mysql.connector.connect(host=self.host, user=self.user, passwd=self.password, database=self.database)
            cursor = connection.cursor(buffered=True)
            createSQL = "INSERT IGNORE INTO bot (server, translation) VALUES (%s, %s)"
            updateSQL = "UPDATE bot SET translation = %s WHERE server = %s"
            cursor.execute(createSQL, (ctx.message.guild.id, translation))
            cursor.execute(updateSQL, (translation, ctx.message.guild.id))
            connection.commit()
            connection.close()

            await ctx.send(f"**Successfully updated default translation to `{translation}`!**")

        except:
            await ctx.send(INVALID_TRANSLATION)

    @commands.command(name="quran")
    async def quran(self, ctx, ref: str, edition: str = None):
        async with ctx.channel.typing():

            # If no translation was specified, find a translation to use.
            if edition is None:
                try:
                    edition = self.getGuildTranslation(ctx.message.guild.id)
                    edition = self.formatEdition(edition)
                except AttributeError:
                    edition = 85

            # If a translation was specified in the command, check whether it is valid:
            else:
                try:
                    edition = self.formatEdition(edition)
                except KeyError:
                    return await ctx.send(INVALID_TRANSLATION)

            # Check if the verses need to be fetched from quran.com.
            quranCom = self.isQuranCom(edition)

            # Now fetch the verses:
            try:
                quranSpec = self.getSpec(ref, edition)

            except:
                return await ctx.send(INVALID_ARGUMENTS_ENGLISH.format(prefix))

            surah_name, readableEdition, revelationType = await self.getMetadata(quranSpec, edition)
            translatedSurahName = await self.getTranslatedSurahName(quranSpec, edition)

            if revelationType == "makkah":
                revelationType = "Meccan"
            elif revelationType == "madinah":
                revelationType = "Medinan"

            await self.getVerses(quranSpec, quranCom)

            em = makeEmbed(fields=quranSpec.orderedDict, author=f"Surah {surah_name} ({translatedSurahName})",
                           author_icon=icon, colour=0x048c28, inline=False)
            em.set_footer(text=f'Translation: {readableEdition} | {revelationType}')

            if len(em) > 6000:
                await ctx.send("This passage was too long to send.")

            else:
                await ctx.send(embed=em)

    @commands.command(name="aquran")
    async def aquran(self, ctx, *, ref: str):
        try:
            quranSpec = self.getSpec(ref)
        except:
            return await ctx.send(INVALID_ARGUMENTS_ARABIC.format(prefix))

        surah_name = await self.getMetadata(quranSpec, edition='ar')
        await self.getVerses(quranSpec, False)

        em = makeEmbed(fields=quranSpec.orderedDict, author=f' سورة {surah_name}', author_icon=icon, colour=0x048c28,
                       inline=False)
        await ctx.send(embed=em)

    @staticmethod
    def getSpec(ref, edition = 'ar'):
        surah, min_ayah, max_ayah = processRef(ref)
        return QuranSpecifics(surah, min_ayah, max_ayah, edition)

    """
    Contacts the MySQL database to see if the server set a default transltion.
    If it hasn't, then we use the bot's default one.
    """
    def getGuildTranslation(self, guildID):
        try:
            connection = mysql.connector.connect(host=self.host, user=self.user, passwd=self.password,
                                                 database=self.database)
            cursor = connection.cursor(buffered=True)
            cursor.execute(f"SELECT translation FROM bot WHERE server = {guildID}")
            result = cursor.fetchone()[0]
            connection.close()
        except:
            result = 'haleem'
        return result

    """
    Fetches the verses' text.
    We use the quran.com API or GlobalQuran API depending on the translation used. 
    """
    async def getVerses(self, spec, quranCom):
        for verse in range(spec.minAyah, spec.maxAyah):
            if spec.edition == 'ar':
                async with self.session.get(f'http://api.quran.com:3000/api/v3/chapters/{spec.surah}/verses?page=1&limi'
                                            f't=1&offset={verse - 1}') as r:
                    data = await r.json()
                try:
                    data = data['verses'][0]['text_madani']
                except IndexError:  # This is triggered if the verse doesn't exist.
                    return
                await self.makeOrderedDict(spec, verse, data)
            elif quranCom is False:
                async with self.session.get(self.url1.format(spec.surah, verse, spec.edition)) as r:
                    data = await r.json()
                try:
                    data = data['data']['text']
                except IndexError:  # This is triggered if the verse doesn't exist.
                    return
                await self.makeOrderedDict(spec, verse, data)
            else:
                async with self.session.get(self.url2.format(spec.surah, verse - 1, spec.edition)) as r:
                    data = await r.json()
                try:
                    data = data['verses'][0]['translations'][0]['text']
                    data = re.sub('<[^<]+?>', '', data)
                    data = re.sub('[0-9]', '', data)
                except IndexError:  # This is triggered if the verse doesn't exist.
                    return
                await self.makeOrderedDict(spec, verse, data)

    """
    Make an ordered dict from the verse text.
    The verse text is truncated if it is too long for the embed field. 
    """
    async def makeOrderedDict(self, spec, verse, data):
        if spec.edition == 'ar':
            if len(data) <= 1024:
                spec.orderedDict['{}:{}'.format(convertToArabicNumber(str(spec.surah)), convertToArabicNumber(str(verse)))] = data
            else:
                spec.orderedDict['{}:{}'.format(convertToArabicNumber(str(spec.surah)), convertToArabicNumber(str(verse)))] = data[0:1021] + '...'

        else:
            if len(data) <= 1024:
                spec.orderedDict['{}:{}'.format(spec.surah, verse)] = data
            else:
                spec.orderedDict['{}:{}'.format(spec.surah, verse)] = data[0:1021] + '...'

    """
    Get the surah name in Arabic along with the revelation location.
    """
    async def getMetadata(self, spec, edition):
        if spec.edition == 'ar':
            async with self.session.get(f'http://api.quran.com/api/v3/chapters/{spec.surah}') as r:
                data = await r.json()
                return data['chapter']['name_arabic']
        elif self.isQuranCom(edition):  # This will be true if we're using a quran.com translation
            async with self.session.get(f'http://api.quran.com/api/v3/chapters/{spec.surah}') as r:
                data = await r.json()
                return data['chapter']['name_simple'], self.getEditionName(edition), data['chapter'][
                    'revelation_place']
        else:
            async with self.session.get(f'http://api.alquran.cloud/ayah/{spec.surah}:{spec.minAyah}/{spec.edition}') as r:
                data = await r.json()
                return data['data']['surah']['englishName'], data['data']['edition']['name'], data['data']['surah'][
                    'revelationType']

    async def getTranslatedSurahName(self, spec, edition):
        try:
            languageCode = self.getLanguageCode(edition)
        except KeyError:
            languageCode = None
        async with self.session.get(f'http://api.quran.com/api/v3/chapters/{spec.surah}?language={languageCode}') as r:
            data = await r.json()
            return data['chapter']['translated_name']['name']


# Register as cog
def setup(bot):
    bot.add_cog(Quran(bot))

