from aiohttp import ClientSession
from discord.ext import commands
from discord.ext.commands import has_permissions
from utils import makeEmbed
import re
import mysql.connector
from helpers import processRef, Specifics, prefix

icon = 'http://lh5.ggpht.com/2BfAv_esGGNfXvkhNiwA-77S7145Z7zDGui98OMG2XqBNqjHx7t4Ya-uLZkuynroQ6M=w300'
mysqlDetails = open('mysql.txt').read().splitlines()

class QuranSpecifics(Specifics):
    def __init__(self, surah, minayah, maxayah, edition):
        super().__init__(surah, minayah, maxayah)
        self.edition = edition

class Quran(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.session = ClientSession(loop=bot.loop)
        self.url1 = 'http://api.alquran.cloud/ayah/{}:{}/{}'
        self.url2 = 'http://staging.quran.com:3000/api/v3/chapters/{}/verses?page=1&limit=1&offset={}&translations[]={}'
        self.quranComEditions = ['haleem', 'taqiusmani', 'clearquran', 85, 84, 131]
        self.host = mysqlDetails[0]
        self.user = mysqlDetails[1]
        self.password = mysqlDetails[2]
        self.database = mysqlDetails[3]



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
            'haleem': 85,
            'taqiusmani': 84,
            'clearquran': 131,
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
            'indonesian': 'id.indonesian',
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
            85: 'Muhammad A. S. Abdel Haleem',
            131: "Dr. Mustafa Khattab, The Clear Qur'an",
            84: "Mufti Taqi Usmani"
        }
        return editionNames[edition]

    @commands.command(name="aquran")
    async def aquran(self, ctx, *, ref: str):

        try:
            quranSpec = self.getSpec(ref)
        except:
            await ctx.send("Invalid arguments! Do `{0}aquran [surah]:[ayah]`. "
                               "Example: `{0}aquran 1:1`"
                               "\n"
                               "To quote multiple verses, do `{0}quran [surah]:[first ayah]-[last ayah]`"
                               "\n"
                               "Example: `{0}aquran 1:1-7`.".format(prefix))
            return

        surah_name = await self.getMetadata(quranSpec, edition = 'ar')
        await self.getVerses(quranSpec, quranCom = False)

        em = makeEmbed(fields=quranSpec.orderedDict, author=surah_name, author_icon=icon, colour=0x78c741, inline=False)
        await ctx.send(embed=em)

    @commands.command(name="settranslation")
    @has_permissions(manage_guild=True)
    async def settranslation(self, ctx, translation: str):

        if translation is None:
            await ctx.send("You must provide a valid translation key. List of translation keys: <https://github.com/galacticwarrior9/islambot/blob/master/Translations.md>")
            return

        else:

            try:
                
                db = mysql.connector.connect(host=self.host, user=self.user, passwd=self.password, database=self.database)
                Quran.formatEdition(translation)
                server = ctx.message.guild.id
                cursor = db.cursor(buffered=True)
                query = (f"UPDATE bot SET translation = %s WHERE server = %s")
                data = (translation, server)
                cursor.execute(query, data)
                db.commit()
                cursor.close()

                await ctx.send(f"**Successfully updated default translation to `{translation}`!**")

            except Exception as e:
                await ctx.send("**Invalid translation key**. List of translation keys: <https://github.com/galacticwarrior9/islambot/blob/master/Translations.md>")

    @commands.command(name="quran")
    async def quran(self, ctx, ref: str, edition: str = None):

        db = mysql.connector.connect(host=self.host, user=self.user, passwd=self.password, database=self.database)
        server = ctx.message.guild.id
        cursor = db.cursor(buffered=True)
        sql = "INSERT IGNORE INTO bot (server, translation) VALUES (%s, %s)"
        val = (f"{server}", "sahih")
        cursor.execute(sql, val)
        db.commit()

        if edition is None:
            cursor.execute(f"SELECT translation FROM bot WHERE server = {server}")
            edition = str(cursor.fetchone()[0])
            print(edition)
        cursor.close()
        edition = edition.lower()

        if edition in self.quranComEditions:
            quranCom = True

        else:
            quranCom = False

        try:
            edition = self.formatEdition(edition)

            try:
                quranSpec = self.getSpec(ref, edition=edition)

            except:

                await ctx.send("Invalid arguments! Do `{0}quran [surah]:[ayah] [edition]`. "
                               "Example: `{0}quran 1:1`"
                               "\n"
                               "Example 2: `{0}quran 1:1 yusufali`"
                               "\n\n"
                               "To quote multiple verses, do `{0}quran [surah]:[first ayah]-[last ayah]`"
                               "\n"
                               "Example: `{0}quran 1:1-7`.".format(prefix))
                return

            try:

                surah_name, readableEdition, englishSurahName, revelationType = await self.getMetadata(quranSpec, edition)

                await self.getVerses(quranSpec, quranCom)

                em = makeEmbed(fields=quranSpec.orderedDict, author=f"Surah {surah_name} ({englishSurahName})",
                               author_icon=icon, colour=0x78c741, inline=False)
                em.set_footer(text=f'Translation: {readableEdition} | {revelationType}')
                await ctx.send(embed=em)

            except Exception as e:

                print(e)

        except:
            await ctx.send(f'Invalid translation. A list can be found at:\n'
                            '<https://github.com/galacticwarrior9/islambot/blob/master/Translations.md>')

    @staticmethod
    def getSpec(ref, edition = 'ar'):
        surah, min_ayah, max_ayah = processRef(ref)
        return QuranSpecifics(surah, min_ayah, max_ayah, edition)

    async def getVerses(self, spec, quranCom):
        for verse in range(spec.minAyah, spec.maxAyah):
            if quranCom == False:
                async with self.session.get(self.url1.format(spec.surah, verse, spec.edition)) as r:
                    data = await r.json()
                spec.orderedDict['{}:{}'.format(spec.surah, verse)] = data['data']['text']
            else:
                async with self.session.get(self.url2.format(spec.surah, verse - 1, spec.edition)) as r:
                    data = await r.json()
                data = data['verses'][0]['translations'][0]['text']
                data = re.sub('<[^<]+?>', '', data)
                data = re.sub('[0-9]', '', data)
                spec.orderedDict['{}:{}'.format(spec.surah, verse)] = data


    async def getMetadata(self, spec, edition):
        async with self.session.get(self.url1.format(spec.surah, spec.minAyah, spec.edition)) as r:
            data = await r.json()
        if spec.edition == 'ar':
            return data['data']['surah']['name']
        elif spec.edition in self.quranComEditions:
            return data['data']['surah']['englishName'], self.getEditionName(edition), data['data']['surah']['englishNameTranslation'], data['data']['surah']['revelationType']
        else:
            print(spec.edition)
            return data['data']['surah']['englishName'], data['data']['edition']['name'], data['data']['surah']['englishNameTranslation'], data['data']['surah']['revelationType'],


# Register as cog
def setup(bot):
    bot.add_cog(Quran(bot))
