from discord.ext import commands
from collections import OrderedDict
from utils import makeEmbed
from googleapiclient.discovery import build

icon = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTwwfPBxiymGCrA9khf3vxMkXt_2mDM1Aboz3nTnA8aIYumDzTb'

class Search(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="search")
    async def search(self, ctx, *, arg):

        api_key = open("google-api-key.txt", "r").read()
        cse_id = open("cse-id.txt", "r").read()

        def search(arg, api_key, cse_id, **kwargs):

            service = build("customsearch", "v1", developerKey=api_key)
            res = service.cse().list(q=arg, cx=cse_id, **kwargs).execute()
            return res['items']

        results = search(arg, api_key, cse_id, num=7)
        o = OrderedDict()

        for result in results:
            title = result['title']
            o['{}'.format(title)] = result['link']

        em = makeEmbed(fields=o, author=f'Results for {arg.title()}', author_icon=icon, colour=0x78c741, inline= False)
        await ctx.send(embed=em)


# Register as cog
def setup(bot):
    bot.add_cog(Search(bot))