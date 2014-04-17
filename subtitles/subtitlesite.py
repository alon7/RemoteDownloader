# -*- coding: utf-8 -*-

import ConfigParser
from abc import ABCMeta
from utils.urlHandler import URLHandler
from os import path
from sys import exit, path as sys_path
from importlib import import_module

SUBTITLE_SITE_LIST = ['SubsCenter', 'SubtitleCoIl']


class SubtitleSite(object):
    __metaclass__ = ABCMeta

    def __init__(self, domainName):
        self.domain = domainName
        self.urlHandler = URLHandler()
        self.configuration = ConfigParser.RawConfigParser()
        self.configuration.readfp(open(r"C:\Users\Public\Documents\utorrent\uTorrent.Py\configuration\subtitlesConfig.cfg"))  # ?

    def downloadSubtitle(self, subtitleResult):
        fileData = self.urlHandler.request(subtitleResult['Domain'], subtitleResult['DownloadPage'])
        self.manageSubtileFile(fileData, subtitleResult['VerSum'] + '.zip')

    @staticmethod
    def manageSubtileFile(fileData, fileName):
        #TODO: unzip files!
        with open(fileName, "wb") as subFile:
            subFile.write(fileData)
        subFile.close()

    @staticmethod
    def classFactory(class_name):
        class_lower_name = class_name.lower()

        if class_name in SUBTITLE_SITE_LIST:
            engines_path = path.dirname(__file__)
            if engines_path not in sys_path:
                sys_path.insert(0, engines_path)

            subtitle_module = import_module(class_lower_name)
            subtitle_class = getattr(subtitle_module, class_name)

            return subtitle_class()
