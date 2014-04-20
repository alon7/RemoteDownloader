from bs4 import BeautifulSoup
import re
from utils.urlHandler import URLHandler


class PUBLICHD_PAGES:
    DOMAIN = 'https://publichd.se'
    SEARCH = '/index.php?page=torrents&active=0&search=%s&order=5&by=2'


class PublicHD(object):
    http_time_between_calls = 0
    def __init__(self):
        self.urlHandler = URLHandler()

    def search(self, contentToDownload):
        results = []
        data = self.urlHandler.request(PUBLICHD_PAGES.DOMAIN, PUBLICHD_PAGES.SEARCH % (contentToDownload.modifiedName.replace(' ', '%20')))

        if data:
                soup = BeautifulSoup(data)
                results_table = soup.find('table', attrs={'id': 'bgtorrlist2'})
                entries = results_table.find_all('tr')

                for result in entries[2:len(entries) - 1]:
                    info_url = result.find(href=re.compile('torrent-details'))
                    download = result.find(href=re.compile('magnet:'))

                    if info_url and download:
                        results.append({
                            'name': str(info_url.string),
                            'size': str(result.find_all('td')[7].string),
                            'seeders': int(result.find_all('td')[4].string),
                            'leechers': int(result.find_all('td')[5].string),
                            'link': download['href']
                        })
        return results