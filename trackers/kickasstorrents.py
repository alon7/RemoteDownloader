import json
from utils.urlHandler import URLHandler
from utils.Utils import bytes_converter


class KICKASSTORRENT_PAGES:
    DOMAIN = 'https://kickass.to'
    SEARCH = '/json.php?q={0}%20seeds:1&field=seeders&sorder=desc'  # minimum seeders 1 should be dynamic!


class KickAssTorrents(object):
    supported_categories = {'all': '', 'movies': 'Movies', 'tv': 'TV', 'music': 'Music', 'games': 'Games',
                            'software': 'Applications'}

    def __init__(self):
        self.urlHandler = URLHandler()

    def search(self, contentToDownload):
        results = []
        json_data = self.urlHandler.request(KICKASSTORRENT_PAGES.DOMAIN, KICKASSTORRENT_PAGES.SEARCH.format(contentToDownload.modifiedName.replace(' ', '%20')))
        json_dict = json.loads(json_data)
        torrentList = json_dict['list']
        for torrent in torrentList:
                results.append({
                'name': str(torrent['title']),
                'size': bytes_converter(torrent['size'], size_or_speed='size'),
                'seeders': int(torrent['seeds']),
                'leechers': int(torrent['leechs']),
                'link': torrent['torrentLink']
                })
        return results
