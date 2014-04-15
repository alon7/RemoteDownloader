from bs4 import BeautifulSoup
import re
import traceback
import six
from utils.urlHandler import URLHandler


class THEPIRATEBAY_PAGES:
    DOMAIN = 'https://thepiratebay.se'
    SEARCH = '/search/%s/%s/7/0'  # minimum seeders 1 should be dynamic!


class ThePirateBay(object):
    def __init__(self):
        self.urlHandler = URLHandler()

    def search(self, contentToDownload):
        page = 0
        total_pages = 1
        results  = []
        while page < total_pages:

            data = self.urlHandler.request(THEPIRATEBAY_PAGES.DOMAIN, THEPIRATEBAY_PAGES.SEARCH % (contentToDownload.modifiedName.replace(' ', '%20'), page))
            page += 1

            if data:
                try:
                    soup = BeautifulSoup(data)
                    results_table = soup.find('table', attrs = {'id': 'searchResult'})

                    if not results_table:
                        return

                    total_pages = len(soup.find('div', attrs = {'align': 'center'}).find_all('a'))
                    entries = results_table.find_all('tr')
                    for result in entries[2:]:
                        link = result.find(href = re.compile('torrent\/\d+\/'))
                        download = result.find(href = re.compile('magnet:'))

                        size = re.search('Size (?P<size>.+),', six.text_type(result.select('font.detDesc')[0])).group('size')

                        if link and download:
                            results.append({
                                'name': link.string,
                                'size': size,
                                'seeders': result.find_all('td')[2].string,
                                'leechers': result.find_all('td')[3].string,
                                'link': download['href'],
                            })
                except Exception, e:
                    print e
        return results