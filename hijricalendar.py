import aiohttp
import discord
from helpers import get_site_source
from discord.ext import commands, tasks


class HijriCalendar(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=bot.loop)
        self.toGregorian_url = 'https://api.aladhan.com/hToG?date={}'
        self.toHijri_url = 'https://api.aladhan.com/gToH?date={}'
        self.current_hijri_url = 'https://www.islamicfinder.org/islamic-date-converter/'
        self.updateHijriDate.start()

    @commands.command(name='convertfromhijri')
    async def converthijridate(self, ctx, date: str):

        # Check if the date is in a DD-MM-YY format
        if not self.isInCorrectFormat(date):
            await ctx.send  ('Invalid arguments! Do `-converthijridate DD-MM-YY`.\n\n'
                               'Example: `-converthijridate 17-01-1407`(for 17 Muharram 1407)')
            return

        try:
            day, month, year = await self.getConvertedDate(date, getHijri = False)
            await ctx.send(f'The hijri date {date} is **{day} {month} {year} CE.**')

        except:
            await ctx.send('An error occurred when trying to convert the date.')

    @commands.command(name='converttohijri')
    async def convertdate(self, ctx, date: str):

        # Check if the date is in a DD-MM-YY format
        if not self.isInCorrectFormat(date):
            await ctx.send(
                'Invalid arguments! Do `-convertdate DD-MM-YY`.\n\n'
                'Example: `-convertdate 17-01-2001`')
            return

        try:
            day, month, year = await self.getConvertedDate(date)
            await ctx.send(f'The date {date} is **{day} {month} {year} AH.**')

        except:
            await ctx.send('An error occurred when trying to convert the date.')

    @commands.command(name='hijridate')
    async def hijridate(self, ctx):

        date = await self.getCurrentHijriDate()
        await ctx.send(f'Today is **{date}**.')

    async def getConvertedDate(self, date, getHijri = True):

        if getHijri:
            url = self.toHijri_url

        else:
            url = self.toGregorian_url

        async with self.session.get(url.format(date)) as r:
            data = await r.json()

        if getHijri:
            calendar = data['data']['hijri']
        else:
            calendar = data['data']['gregorian']

        day = calendar['month']['number']
        month = calendar['month']['en']
        year = calendar['year']

        return day, month, year

    async def getCurrentHijriDate(self):

        content = await get_site_source(self.current_hijri_url)
        date = content.find('span', attrs={'class':'date-converted-date'})
        date = date.text[:-1] + " AH"
        date = date.replace(',', '')\
            .replace('Shaban', 'Shaʿbān') \
            .replace('Ramadan', 'Ramaḍān') \
            .replace('Shawwal', 'Shawwāl') \
            .replace('Dhul Qadah', 'Dhū al-Qa‘dah') \
            .replace('Dhul Hijjah', 'Dhū al-Ḥijjah')
        return date

    @tasks.loop(hours=1)
    async def updateHijriDate(self):
        date = await self.getCurrentHijriDate()
        game = discord.Game(f"-ihelp | {date}")
        await self.bot.change_presence(activity=game)

    @staticmethod
    def isInCorrectFormat(date):
        try:
            date.split('-')
            return True
        except:
            return False


# Register as cog
def setup(bot):
    bot.add_cog(HijriCalendar(bot))
