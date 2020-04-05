from collections import OrderedDict
import aiohttp
from bs4 import BeautifulSoup

prefix = '-'


async def get_site_source(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            text = await resp.read()

    return BeautifulSoup(text.decode('utf-8','ignore'), 'html.parser')


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

    return [surah, min_ayah, max_ayah]