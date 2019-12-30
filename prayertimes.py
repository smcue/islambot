import discord
from discord.ext import commands
from aiohttp import ClientSession
icon = 'https://www.muslimpro.com/img/muslimpro-logo-2016-250.png'

headers = {'content-type': 'application/json'}

class PrayerTimes(commands.Cog):

    def __init__(self, bot):
        self.session = ClientSession(loop = bot.loop)
        self.bot = bot
        self.hanafi_url = 'http://api.aladhan.com/timingsByAddress?address={0}&method=4&school=1'
        self.default_url = 'http://api.aladhan.com/timingsByAddress?address={0}&method=4&school=0'

    @commands.command(name="prayertimes")
    async def prayertimes(self, ctx, *, location):

        try:
            # Open URL and parse JSON
            async with self.session.get(self.default_url.format(location, '0'), headers=headers) as resp:
                data = await resp.json()

            # Assign variables from JSON
            fajr = data['data']['timings']['Fajr']
            sunrise = data['data']['timings']['Sunrise']
            dhuhr = data['data']['timings']['Dhuhr']
            default_asr = data['data']['timings']['Asr']
            maghrib = data['data']['timings']['Maghrib']
            isha = data['data']['timings']['Isha']
            imsak = data['data']['timings']['Imsak']
            midnight = data['data']['timings']['Midnight']

            async with self.session.get(self.hanafi_url.format(location, '1'), headers=headers) as resp:
                data = await resp.json()

            hanafi_asr = data['data']['timings']['Asr']

            # Construct message from variables
            text = f'**Fajr**: {fajr}\n' \
                   f'**Sunrise**: {sunrise}\n' \
                   f'**Dhuhr**: {dhuhr}\n' \
                   f'**Asr**: {default_asr} | **Asr (Hanafi)**: {hanafi_asr}\n' \
                   f'**Maghrib**: {maghrib}\n' \
                   f'**Isha**: {isha}\n' \
                   f'**Midnight**: {midnight}\n' \
                   f'**Imsak**: {imsak}'

            # Construct and send embed
            em = discord.Embed(description=text, colour=0x2186d3)
            em.set_author(name=f'Prayer Times for {location.title()}', icon_url=icon)
            em.set_footer(text=f'Calculation Method: Umm al-Qura')
            await ctx.send(embed=em)


        except:

            await ctx.send('**Invalid arguments!** Usage: `.prayertimes [location]`.\n'
                               'Example: `-prayertimes London`\n')


# Register as cog
def setup(bot):
    bot.add_cog(PrayerTimes(bot))
