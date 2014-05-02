from content import Content
from utils import Utils
from subtitles.subtitlesite import SubtitleSite, SUBTITLE_SITE_LIST
from trackers.tracker import TrackerSite, TRACKER_SITE_LIST
from uTorrent.UTorrentClient import UTorrentClient
from uTorrent.TorrentFile import TorrentFile
import threading
import Queue
import time


class CostumeThread(threading.Thread):
    def __init__(self, queue, results, subsOrTorrent):
        threading.Thread.__init__(self)
        self.queue = queue
        self.subsOrTorrent = subsOrTorrent
        if "subs" == subsOrTorrent:
            self.subResults = results
        elif "torrents" == subsOrTorrent:
            self.torrentResults = results

    def run(self):
        while True:
            scraper, func, content = self.queue.get()
            f = getattr(scraper.__class__, func)
            res = f(scraper, content)
            if "subs" == self.subsOrTorrent:
                self.subResults.extend(res)
            elif "torrents" == self.subsOrTorrent:
                self.torrentResults.extend(res)

            self.queue.task_done()


def getALL(trackers, subtitlesSites, contentToDownload):
    queue = Queue.Queue()
    subResults = []
    trackerResults = []

    combinedScrapersList = [(subtitlesSite, "findSubtitles", contentToDownload, subResults, "subs") for subtitlesSite in subtitlesSites] + [(tracker, "search", contentToDownload, trackerResults, "torrents") for tracker in trackers]
    for scraper in combinedScrapersList:
        th = CostumeThread(queue, scraper[3], scraper[4])
        th.setDaemon(True)
        th.start()
    for scraper in combinedScrapersList:
        queue.put((scraper[0], scraper[1], scraper[2]))
    queue.join()
    return subResults, trackerResults


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


def getMatches(torrents, subs):
    matches = []
    for torrent in torrents:
        for sub in subs:
            if Utils.versionMatching(torrent.get('name'), sub.get('VerSum')):
                matches.append((torrent, sub))
                break
    return matches


if __name__ == "__main__":
    start = time.time()  # just for debugging - should be removed
    c = Content("silicon valley", "series", season='1', episodeNumber='1')
    subtitleSites = [SubtitleSite.classFactory(site) for site in SUBTITLE_SITE_LIST]
    trackerSites = [TrackerSite.classFactory(site) for site in TRACKER_SITE_LIST]

    a,b = getALL(trackerSites, subtitleSites, c)
    matches = getMatches(b, a)

    end = time.time() - start
    print end
    #downloadContent(c)

    #ut.add_url(c.match[0][0].get('link'))
    #SubtitleSite.downloadSubtitle(c.match[0][1])