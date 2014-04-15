# -*- coding: utf-8 -*-

import ConfigParser
from abc import ABCMeta

from utils.urlHandler import URLHandler


class SubtitleSite(object):
    __metaclass__ = ABCMeta

    def __init__(self, domainName):
        self.domain = domainName
        self.urlHandler = URLHandler()
        self.configuration = ConfigParser.RawConfigParser()
        self.configuration.readfp(open(r"C:\Users\Public\Documents\utorrent\uTorrent.Py\configuration\subtitlesConfig.cfg"))  # ?

    def downloadSubtitle2(self):
        pass

    @staticmethod
    def manageSubtileFile(fileData, fileName):
        #TODO: unzip files!
        with open(fileName, "wb") as subFile:
            subFile.write(fileData)
        subFile.close()