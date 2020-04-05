import aiohttp
from discord.ext import commands


class HijriCalendar(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=bot.loop)
        self.toGregorian_url = 'https://api.aladhan.com/hToG?date={}'
        self.toHijri_url = 'https://api.aladhan.com/gToH?date={}'

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
