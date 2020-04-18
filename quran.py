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

icon = 'http://lh5.ggpht.com/2BfAv_esGGNfXvkhNiwA-77S7145Z7zDGui98OMG2XqBNqjHx7t4Ya-uLZkuynroQ6M=w300'


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
        self.quranComEditions = ['haleem', 'taqiusmani', 'khattab', 'amharic',
                                 'chechen', 'finnish', 'indonesian', 'ghali'
                                 'tajik', 85, 84, 101, 17, 30, 33, 74, 106, 87]
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
            'bosnian': 'bs.mlivo',
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
            'sahih': 'en.sahih',
            'ahmedali': 'en.ahmedali',
            'arberry': 'en.arberry',
            'asad': 'en.asad',
            'daryabadi': 'en.daryabadi',
            'hilali': 'en.hilali',
            'pickthall': 'en.pickthall',
            'qaribullah': 'en.qaribullah',
            'sarwar': 'en.sarwar',
            'yusufali': 'en.yusufali',
            'shakir': 'en.shakir',
            'transliteration': 'en.transliteration',
            'spanish': 'es.cortes',
            'ansarian': 'fa.ansarian',
            'ayati': 'fa.ayati',
            'fooladvand': 'fa.fooladvand',
            'ghomshei': 'fa.ghomshei',
            'makarem': 'fa.makarem',
            'french': 'fr.hamidullah',
            'hausa': 'ha.gumi',
            'hindi': 'ha.hindi',
            'italian': 'it.piccardo',
            'japanese': 'ja.japanese',
            'korean': 'ko.korean',
            'kurdish': 'ku.asan',
            'malayalam': 'ml.malayalam',
            'dutch': 'nl.keyzar',
            'norwegian': 'no.berg',
            'polish': 'pl.bielawskiego',
            'portuguese': 'pt.elhayek',
            'romanian': 'ro.grigore',
            'kuliev': 'ru.kuliev',
            'osmanov': 'ru.osmanov',
            'porokhova': 'ru.porokhova',
            'sindhi': 'sd.amroti',
            'somali': 'so.abduh',
            'ahmeti': 'sq.ahmeti',
            'mehdiu': 'sq.mehdiu',
            'nahi': 'sq.nahi',
            'swedish': 'sv.bernstrom',
            'swahili': 'sw.barwani',
            'tamil': 'ta.tamil',
            'thai': 'th.thai',
            'ates': 'tr.ates',
            'bulac': 'tr.bulac',
            'turkish': 'tr.diyanet',
            'diyanet': 'tr.diyanet',
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
            'maududi': 'ur.maududi',
            'malay': 'ms.basmeih',
            'uzbek': 'uz.sodik',
            'chinese': 'zh.jian'
        }
        return editionDict[edition]

    @staticmethod
    def getEditionName(edition):
        editionNames = {
            85: 'Abdel Haleem',
            101: "Dr. Mustafa Khattab",
            84: "Mufti Taqi Usmani",
            17: "Dr. Ghali",
            30: "Finnish",
            33: "Indonesian (Ministry of Religious Affairs)",
            74: "Tajik (Abdolmohammad Ayati)",
            106: "Chechen (Magomed Magomedov)",
            87: "Amharic (Sadiq and Sani)"
        }
        return editionNames[edition]

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
                edition = self.getGuildTranslation(ctx.message.guild.id)

            # If a translation was specified in the command, check whether it is valid:
            else:
                try:
                    edition = self.formatEdition(edition)
                except KeyError:
                    await ctx.send(INVALID_TRANSLATION)
                    return

            # Check if the verses need to be fetched from quran.com.
            if edition in self.quranComEditions:
                quranCom = True
            else:
                quranCom = False

            # Now fetch the verses:
            try:
                quranSpec = self.getSpec(ref, edition)

            except:
                await ctx.send(INVALID_ARGUMENTS_ENGLISH.format(prefix))
                return

            surah_name, readableEdition, englishSurahName, revelationType = await self.getMetadata(quranSpec, edition)

            await self.getVerses(quranSpec, quranCom)

            em = makeEmbed(fields=quranSpec.orderedDict, author=f"Surah {surah_name} ({englishSurahName})",
                           author_icon=icon, colour=0x78c741, inline=False)
            em.set_footer(text=f'Translation: {readableEdition} | {revelationType}')
            await ctx.send(embed=em)

    @commands.command(name="aquran")
    async def aquran(self, ctx, *, ref: str):
        try:
            quranSpec = self.getSpec(ref)
        except:
            await ctx.send(INVALID_ARGUMENTS_ARABIC.format(prefix))
            return

        surah_name = await self.getMetadata(quranSpec, edition='ar')
        await self.getVerses(quranSpec, False)

        em = makeEmbed(fields=quranSpec.orderedDict, author=f'{surah_name}', author_icon=icon, colour=0x78c741, inline=False)
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
        result = self.formatEdition(result)
        return result

    """
    Fetches the verses' text.
    We use the quran.com API or GlobalQuran API depending on the translation used. 
    """
    async def getVerses(self, spec, quranCom):
        for verse in range(spec.minAyah, spec.maxAyah):
            if quranCom is False:
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
    Get the surah name in Arabic and English along with the verse revelation type.
    """
    async def getMetadata(self, spec, edition):
        async with self.session.get(self.url1.format(spec.surah, spec.minAyah, spec.edition)) as r:
            data = await r.json()
        if spec.edition == 'ar':
            return data['data']['surah']['name']
        elif spec.edition in self.quranComEditions:
            return data['data']['surah']['englishName'], self.getEditionName(edition), data['data']['surah']['englishNameTranslation'], data['data']['surah']['revelationType']
        else:
            return data['data']['surah']['englishName'], data['data']['edition']['name'], data['data']['surah']['englishNameTranslation'], data['data']['surah']['revelationType'],


# Register as cog
def setup(bot):
    bot.add_cog(Quran(bot))

