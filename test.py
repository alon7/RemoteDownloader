from content import Content
from utils import Utils
from subtitles.subtitlesite import SubtitleSite, SUBTITLE_SITE_LIST
from trackers.tracker import TrackerSite, TRACKER_SITE_LIST
from uTorrent.UTorrentClient import UTorrentClient
from uTorrent.TorrentFile import TorrentFile

def downloadContent(contentToDownload):
    uTorrentClient = UTorrentClient()
    matchingTorrent, matchingSubtitle = contentToDownload.match[0]
    uTorrentClient.add_url(matchingTorrent.get('link'))
    torrentList = uTorrentClient.list()
    for torrent in torrentList[1].get('torrents'):
        torrentFile = TorrentFile(torrent)
        if Utils.versionMatching(torrentFile.name, matchingTorrent.get('name')):
            torrentPath = torrentFile.path
            a = uTorrentClient.getfiles(torrentFile.hash)
            contnerFileName = sorted(uTorrentClient.getfiles(torrentFile.hash)[1].get('files')[1], key=lambda x: x[1])[-1][0]
            break
    SubtitleSite.downloadSubtitle(matchingSubtitle, torrentPath, contnerFileName)


def findsubtitles(subtitleSites, contentToDownload):
    for site in subtitleSites:
        contentToDownload = site.findSubtitles(contentToDownload)
    contentToDownload.match = sorted(contentToDownload.match, key=lambda x: x[0]['seeders'])[::-1]
    return contentToDownload


def getAllTorrents(trackers, contentToDownload):
    results = []
    for tracker in trackers:
        results.extend(tracker.search(contentToDownload))
    sortedresults = sorted(results, key=lambda k: k['seeders'])[::-1]
    return sortedresults

if __name__ == "__main__":
    c = Content("game of thrones", "series", season='3', episodeNumber='9')
    subtitleSites = [SubtitleSite.classFactory(site) for site in SUBTITLE_SITE_LIST]
    trackerSites = [TrackerSite.classFactory(site) for site in TRACKER_SITE_LIST]

    c.torrents = getAllTorrents(trackerSites, c)
    c = findsubtitles(subtitleSites, c)
    downloadContent(c)

    #ut.add_url(c.match[0][0].get('link'))
    #SubtitleSite.downloadSubtitle(c.match[0][1])

    g = 8