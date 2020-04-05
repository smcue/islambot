from discord.ext import commands
import discord

icon = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTwwfPBxiymGCrA9khf3vxMkXt_2mDM1Aboz3nTnA8aIYumDzTb'

class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ihelp")
    async def ihelp(self, ctx):

        em = discord.Embed(title = 'IslamBot Help', colour = 0x4A90E2, description="For a detailed explanation of the commands, please consult the documentation at https://github.com/galacticwarrior9/islambot", url="https://github.com/galacticwarrior9/islambot")

        em.add_field(name="Qur'an", value='-quran <surah:ayah> <optional translation> *or* -quran <surah:ayah1-ayah2> e.g. `-quran 1:1-7 pickthall` \n -aquran <surah:ayah> *or* -aquran <surah:ayah1-ayah2> e.g. `-aquran 1:1-7` \n -morphology <surah:ayah:word number> e.g. `-morphology 2:1:3` \n -mushaf <surah:ayah> e.g. `-mushaf 1:3:`', inline=False)
        em.add_field(name="Tafsir", value='-tafsir <surah:ayah> <optional tafsir name> e.g. `-tafsir 1:1 ibnkathir`  \n -atafsir <surah:ayah> <tafsir name> e.g. `-atafsir 1:1 razi`', inline=False)
        em.add_field(name="Hadith", value='-hadith <collection name> <book no>:<hadith no> e.g. `-hadith bukhari 1:2` \n -ahadith <collection name> <book no>:<hadith no> e.g. `-ahadith bukhari 1:2`', inline=False)
        em.add_field(name="Prayer Times", value='-prayertimes <Location> e.g. `-prayertimes Burj Khalifa, Dubai`', inline=False)
        em.add_field(name="Hijri Calendar", value='-converttohijri DD-MM-YYYY e.g. `-converttohijri 13-08-2019` \n -convertfromhijri DD-MM-YYYY e.g. `-convertfromhijri 01-02-1440`', inline=False)
        em.add_field(name="Search", value='-search <search term> e.g. `-search Can Hanafis eat shrimp?`', inline=False)
        em.add_field(name="Admin", value='-settranslation <translation> e.g. `-settranslation clearquran` \n **You must have the "Manage Server" permission to use this command**. \n List of translations: https://github.com/galacticwarrior9/islambot/blob/master/Translations.md', inline=False)
        em.set_footer(text="Support Server - https://discord.gg/Ud3MHJR")

        await ctx.send(embed=em)


# Register as cog
def setup(bot):
    bot.add_cog(Help(bot))
