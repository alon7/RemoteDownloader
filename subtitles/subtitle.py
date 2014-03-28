# -*- coding: utf-8 -*-

import ConfigParser
from abc import ABCMeta

from utils.urlHandler import URLHandler


class Subtitle(object):
    __metaclass__ = ABCMeta

    def __init__(self, domainName):
        super(Subtitle, self).__init__()
        self.domain = domainName
        self.urlHandler = URLHandler()
        self.configuration = ConfigParser.RawConfigParser()
        self.configuration.readfp(open(r"C:\Users\Public\Documents\utorrent\uTorrent.Py\configuration\subtitlesConfig.cfg"))  # ?

    @staticmethod
    def manageSubtileFile(fileData, fileName):
        #TODO: unzip files!
        with open(fileName, "wb") as subFile:
            subFile.write(fileData)
        subFile.close()