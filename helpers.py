from collections import OrderedDict
import aiohttp
from bs4 import BeautifulSoup

prefix = '-'


async def get_site_source(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            text = await resp.read()

    return BeautifulSoup(text.decode('utf-8', 'ignore'), 'html.parser')


class Specifics:
    def __init__(self, surah, ayah, maxayah):
        self.surah = surah
        self.minAyah = ayah
        self.maxAyah = maxayah
        self.orderedDict = OrderedDict()


def processRef(ref):
    surah = int(ref.split(':')[0])
    min_ayah = int(ref.split(':')[1].split('-')[0])

    try:
        max_ayah = int(ref.split(':')[1].split('-')[1]) + 1
    except IndexError:
        max_ayah = min_ayah + 1

    # If the min ayah is larger than the max ayah, we assume this is a mistake and swap their values.
    if min_ayah > max_ayah:
        temp = min_ayah
        min_ayah = max_ayah
        max_ayah = temp

    # Embeds can display a maximum of 25 fields (i.e. 25 verses) so we trim the list of verses to fetch accordingly.
    elif max_ayah - min_ayah > 25:
        max_ayah = min_ayah + 25

    return [surah, min_ayah, max_ayah]


def convertToArabicNumber(number_string):
    dic = {
        '0': '۰',
        '1': '١',
        '2': '٢',
        '3': '۳',
        '4': '٤',
        '5': '٥',
        '6': '٦',
        '7': '٧',
        '8': '٨',
        '9': '۹',
        ':': ':'
    }
    return "".join([dic[char] for char in number_string])


def convertFromArabicNumber(number_string):
    dic = {
     '۹': '9',
     '٨': '8',
     '٧': '7',
     '٦': '6',
     '٥': '5',
     '٤': '4',
     '۳': '3',
     '٢': '2',
     '١': '1',
     '۰': '0',
     ':': ':'
    }
    return "".join([dic[char] for char in number_string])

