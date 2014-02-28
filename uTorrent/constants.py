#usage - UITorrentEnum.UI_TORRENT_HASH
#TODO: creae a better enum!


class UITorrentEnum:
    UI_TORRENT_HASH, \
    UI_TORRENT_STATUS, \
    UI_TORRENT_NAME, \
    UI_TORRENT_SIZE, \
    UI_TORRENT_PERCENT_PROGRESS, \
    UI_TORRENT_DOWNLOADED, \
    UI_TORRENT_UPLOADED, \
    UI_TORRENT_RATIO, \
    UI_TORRENT_UPLOAD_SPEED, \
    UI_TORRENT_DOWNLOAD_SPEED, \
    UI_TORRENT_ETA, \
    UI_TORRENT_LABEL, \
    UI_TORRENT_PEERS_CONNECTED, \
    UI_TORRENT_PEERS_IN_SWARM, \
    UI_TORRENT_SEEDS_CONNECTED, \
    UI_TORRENT_SEEDS_IN_SWARM, \
    UI_TORRENT_AVAILABILITY, \
    UI_TORRENT_TORRENT_QUEUE_ORDER, \
    UI_TORRENT_REMAINING = range(19)


class UITorrentStatusEnum:
    UI_TORRENT_STARTED = 1
    UI_TORRENT_CHECKING = 2
    UI_TORRENT_START_AFTER_CHECK = 4
    UI_TORRENT_CHECKED = 8
    UI_TORRENT_ERROR = 16
    UI_TORRENT_PAUSED = 32
    UI_TORRENT_QUEUED = 64
    UI_TORRENT_LOADED = 128


class TorrentFile(object):
    def __init__(self, torrentjson):
        self.hash = torrentjson[UITorrentEnum.UI_TORRENT_HASH]
        self.status = torrentjson[UITorrentEnum.UI_TORRENT_STATUS]
        self.name = torrentjson[UITorrentEnum.UI_TORRENT_NAME]
        self.size = torrentjson[UITorrentEnum.UI_TORRENT_SIZE]
        self.percent_progress = torrentjson[UITorrentEnum.UI_TORRENT_PERCENT_PROGRESS]
        self.downloaded = torrentjson[UITorrentEnum.UI_TORRENT_DOWNLOADED]
        self.uploaded = torrentjson[UITorrentEnum.UI_TORRENT_UPLOADED]
        self.ratio = torrentjson[UITorrentEnum.UI_TORRENT_RATIO]
        self.upload_speed = torrentjson[UITorrentEnum.UI_TORRENT_UPLOAD_SPEED]
        self.download_speed = torrentjson[UITorrentEnum.UI_TORRENT_DOWNLOAD_SPEED]
        self.eta = torrentjson[UITorrentEnum.UI_TORRENT_ETA]
        self.label = torrentjson[UITorrentEnum.UI_TORRENT_LABEL]
        self.peers_connected = torrentjson[UITorrentEnum.UI_TORRENT_PEERS_CONNECTED]
        self.peers_in_swarm = torrentjson[UITorrentEnum.UI_TORRENT_PEERS_IN_SWARM]
        self.seeds_connected = torrentjson[UITorrentEnum.UI_TORRENT_SEEDS_CONNECTED]
        self.seeds_in_swarm = torrentjson[UITorrentEnum.UI_TORRENT_SEEDS_IN_SWARM]
        self.availability = torrentjson[UITorrentEnum.UI_TORRENT_AVAILABILITY]
        self.torrent_queue_order = torrentjson[UITorrentEnum.UI_TORRENT_TORRENT_QUEUE_ORDER]
        self.remaining = torrentjson[UITorrentEnum.UI_TORRENT_REMAINING]

        self.status = self.get_status()

    def get_status(self):
        if self.percent_progress / 10 == 100:
            return "Finished"
        return "good job"
