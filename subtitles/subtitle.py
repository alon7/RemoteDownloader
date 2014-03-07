# -*- coding: utf-8 -*-

import re
import urllib
from subtitles.urlHandler import URLHandler
import ConfigParser
from abc import abstractmethod, ABCMeta


class Subtitle(object):
    __metaclass__ = ABCMeta

    def __init__(self, domainName):
        super(Subtitle, self).__init__()
        self.domain = domainName
        self.urlHandler = URLHandler()
        self.configuration = ConfigParser.RawConfigParser()
        self.configuration.readfp(open(r"C:\Users\Public\Documents\uTorrent.Py\configuration\subtitlesConfig.cfg"))  # ?

    #maybe should be implemented here
    @abstractmethod
    def download_subtitle(self, id, filename):
        pass

    @abstractmethod
    def _is_logged_in(self, url):
        pass

    @abstractmethod
    def login(self):
        pass