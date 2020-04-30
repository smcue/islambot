from discord.ext import commands
import discord

icon = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTwwfPBxiymGCrA9khf3vxMkXt_2mDM1Aboz3nTnA8aIYumDzTb'


class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ihelp")
    async def ihelp(self, ctx, *, section: str = "main"):

        section = section.lower()

        if section == "main":
            em = discord.Embed(title='Help', colour=0x0a519c, description="**Type -ihelp <category>**, e.g. `-ihelp quran`")
            em.add_field(name="Categories", value='\n• Quran\n• Hadith\n• Tafsir\n• Prayer Times\n• Dua\n• Calendar',
                         inline=False)
            em.add_field(name="Information", value="• Code: https://github.com/galacticwarrior9/islambot\n• Documentation: https://github.com/galacticwarrior9/islambot/blob/master/README.md", inline=False)
            em.set_footer(text="Support Server - https://discord.gg/Ud3MHJR")
            await ctx.send(embed=em)

        elif section == "quran":
            em = discord.Embed(title="Qurʼān", colour=0x0a519c, description='Available translations: https://github.com/galacticwarrior9/islambot/blob/master/Translations.md')
            em.add_field(name="-quran", inline=True, value="Gets Qur'anic verses."
                                              "\n\n__Usage__"
                                              "\n\n`-quran <surah>:<ayah> <optional translation>`"
                                              "\n\nExample: `-quran 1:1`"
                                              "\n\n`-quran <surah:<first ayah>-<last ayah> <optional translation>`"
                                              "\n\nExample: `-quran 1:1-7 turkish`")

            em.add_field(name="-aquran", inline=True, value="Gets Qur'anic verses in Arabic."
                                              "\n\n__Usage__"
                                              "\n\n`-aquran <surah>:<ayah>`"
                                              "\n\nExample: `-aquran 1:1`"
                                              "\n\n`-quran <surah>:<first ayah>-<last ayah>`"
                                              "\n\nExample: `-aquran 1:1-7`")

            em.add_field(name="-morphology", inline=True, value="View the morphology of a Qur'anic word."
                                              "\n\n__Usage__"
                                              "\n\n`-morphology <surah>:<ayah>:<word number>`"
                                              "\n\nExample: `-aquran 2:255:1`")

            em.add_field(name="-mushaf", inline=True, value="View a Qur'anic verse on a *mushaf*."
                                              "\n\n__Usage__"
                                              "\n\n`-mushaf <surah>:<ayah>`"
                                              "\n\nExample: `-mushaf 1:1`"
                                              "\n\nAdd 'tajweed' to the end for a page with color-coded tajweed rules."
                                              "\n\nExample: `-mushaf 1:1 tajweed`")

            em.add_field(name="-settranslation", inline=True, value="Changes the default translation for -quran."
                                              "\n\n__Usage__"
                                              "\n\n`-settranslation <translation>`"
                                              "\n\nExample: `-settranslation khattab`"
                                              "\n\nYou must have the **Manage Server** permission to use this command.")

            await ctx.send(embed=em)

        elif section == "tafsir":
            em = discord.Embed(title="Tafsīr", colour=0x0a519c, description='Available tafsirs: https://github.com/galacticwarrior9/islambot/blob/master/Tafsir.md')

            em.add_field(name="-tafsir", inline=True, value="Gets tafsīr in English."
                                              "\n\n__Usage__"
                                              "\n\n`-tafsir <surah>:<ayah> <optional tafsir name>`"
                                              "\n\nExample: `-tafsir 1:1`"
                                              "\n\nExample 2: `-tafsir 1:1 ibnkathir`")

            em.add_field(name="-atafsir", inline=True, value="Gets tafsīr in Arabic."
                                              "\n\n__Usage__"
                                              "\n\n`-atafsir <surah>:<ayah> <optional tafsir name>`"
                                              "\n\nExample: `-atafsir 1:1`"
                                              "\n\nExample 2: `-atafsir 1:1 zamakhshari`")

            await ctx.send(embed=em)

        elif section == "calendar":
            em = discord.Embed(title="Hijri Calendar", colour=0x0a519c)

            em.add_field(name="-hijridate", inline=True, value="Gets the current Hijri date (in the US)")

            em.add_field(name="-converttohijri", inline=True, value="Converts a Gregorian date to its Hijri counterpart."
                                              "\n\n__Usage__"
                                              "\n\n`-converttohijri DD-MM-YYYY`"
                                              "\n\nExample: `-converttohijri 15-01-2020`")

            em.add_field(name="-convertfromhijri", inline=True, value="Converts a Hijri date to its Gregorian counterpart."
                                              "\n\n__Usage__"
                                              "\n\n`-convertfromhijri DD-MM-YYYY`"
                                              "\n\nExample: `-convertfromhijri 15-06-1441`")
            await ctx.send(embed=em)

        elif section == "hadith":
            em = discord.Embed(title="Hadith", colour=0x0a519c, description="These commands fetch hadith from *sunnah.com*.")

            em.add_field(name="-hadith", inline=True, value="Gets a sunnah.com hadith in English."
                                                            "\n\n__Usage__"
                                                            "\n\n`-hadith <collection> <book number>:<hadith number>`"
                                                            "\n\nExample: `-hadith bukhari 97:6` for http://sunnah.com/bukhari/97/6")

            em.add_field(name="-ahadith", inline=True, value="Gets a sunnah.com hadith in Arabic."
                                                            "\n\n__Usage__"
                                                            "\n\n`-ahadith <collection> <book number>:<hadith number>`"
                                                            "\n\nExample: `-ahadith bukhari 97:6` for http://sunnah.com/bukhari/97/6")

            await ctx.send(embed=em)

        elif section == "prayer times":
            em = discord.Embed(title="Prayer Times", colour=0x0a519c)

            em.add_field(name="-prayertimes", inline=True, value="Gets prayer times for a specified location."
                                                                 "\n\n__Usage__"
                                                                 "\n\n`-prayertimes <location>`"
                                                                 "\n\nExample: `-prayertimes Burj Khalifa, Dubai`")

            await ctx.send(embed=em)

        elif section == "dua":
            em = discord.Embed(title="Dua", colour=0x0a519c)
            em.add_field(name="-dualist", inline=True, value="Shows a list of duas.")
            em.add_field(name="-dua", inline=True, value="Gets a dua for a topic."
                                                         "\n\n__Usage__"
                                                         "\n\n`-dua <topic>`"
                                                         "\n\nExample: `-dua forgiveness`"
                                                         "\n\nSee `-dualist` for a list of topics.")
            await ctx.send(embed=em)


# Register as cog
def setup(bot):
    bot.add_cog(Help(bot))
