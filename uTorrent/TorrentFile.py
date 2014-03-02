#TODO: creae a better enum!

import datetime


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
    UI_TORRENT_COMPLETED_DOWNLOAD = 1000


class TorrentFile(object):
    def __init__(self, torrentjson):
        self.hash = torrentjson[UITorrentEnum.UI_TORRENT_HASH]
        self.status = torrentjson[UITorrentEnum.UI_TORRENT_STATUS]  # UITorrentStatusEnum!
        self.name = torrentjson[UITorrentEnum.UI_TORRENT_NAME]
        self.size = bytes_converter(torrentjson[UITorrentEnum.UI_TORRENT_SIZE], 'size')
        self.percent_progress = torrentjson[UITorrentEnum.UI_TORRENT_PERCENT_PROGRESS]
        self.downloaded = bytes_converter(torrentjson[UITorrentEnum.UI_TORRENT_DOWNLOADED], 'size')
        self.uploaded = bytes_converter(torrentjson[UITorrentEnum.UI_TORRENT_UPLOADED], 'size')
        self.ratio = torrentjson[UITorrentEnum.UI_TORRENT_RATIO] / 1000.0  # bad practice
        self.upload_speed = bytes_converter(torrentjson[UITorrentEnum.UI_TORRENT_UPLOAD_SPEED], 'speed')
        self.download_speed = bytes_converter(torrentjson[UITorrentEnum.UI_TORRENT_DOWNLOAD_SPEED], 'speed')
        self.eta = torrentjson[UITorrentEnum.UI_TORRENT_ETA]
        self.label = torrentjson[UITorrentEnum.UI_TORRENT_LABEL]
        self.peers_connected = torrentjson[UITorrentEnum.UI_TORRENT_PEERS_CONNECTED]
        self.peers_in_swarm = torrentjson[UITorrentEnum.UI_TORRENT_PEERS_IN_SWARM]
        self.seeds_connected = torrentjson[UITorrentEnum.UI_TORRENT_SEEDS_CONNECTED]
        self.seeds_in_swarm = torrentjson[UITorrentEnum.UI_TORRENT_SEEDS_IN_SWARM]
        self.availability = torrentjson[UITorrentEnum.UI_TORRENT_AVAILABILITY]
        self.torrent_queue_order = torrentjson[UITorrentEnum.UI_TORRENT_TORRENT_QUEUE_ORDER]
        self.remaining = torrentjson[UITorrentEnum.UI_TORRENT_REMAINING]

        self.full_status = self.get_status()
        self.simplified_eta = self.get_eta()

    def get_status(self):
        if self.percent_progress == UITorrentStatusEnum.UI_TORRENT_COMPLETED_DOWNLOAD:
            return "Completed"
        elif self.status & UITorrentStatusEnum.UI_TORRENT_STARTED:
            return "Started"
        elif self.status & UITorrentStatusEnum.UI_TORRENT_PAUSED:
            return "Paused"
        elif self.status & UITorrentStatusEnum.UI_TORRENT_ERROR:
            return "Error"
        else:
            return "WTF! {0} unknown status code".format(self.status)

    def get_eta(self):
        if self.full_status == "Started":
            return eta_seconds_to_datetime(self.eta)
        else:
            return "N\A"


def eta_seconds_to_datetime(eta):
    return datetime.timedelta(seconds=eta)


def bytes_converter(num, size_or_speed):
    if size_or_speed == 'speed':
        ret_string = "\s"
    elif size_or_speed == 'size':
        ret_string = ""

    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s%s" % (num, x, ret_string)
        num /= 1024.0
