# -*- coding: utf-8 -*-

import ConfigParser
from abc import ABCMeta
from utils.urlHandler import URLHandler
import os
from sys import path as sys_path
from importlib import import_module
import zipfile

SUBTITLE_SITE_LIST = ['SubsCenter', 'SubtitleCoIl']


class SubtitleSite(object):
    __metaclass__ = ABCMeta

    def __init__(self, domainName):
        self.domain = domainName
        self.urlHandler = URLHandler()
        self.configuration = ConfigParser.RawConfigParser()
        self.configuration.readfp(open(r"C:\Users\Public\Documents\uTorrent.Py\configuration\subtitlesConfig.cfg"))  # ?

    @staticmethod
    def downloadSubtitle(subtitleResult, path, contnerFileName):
        fileData = URLHandler().request(subtitleResult['Domain'], subtitleResult['DownloadPage'])
        SubtitleSite.manageSubtileFile(fileData, os.path.join(path, subtitleResult['VerSum'] + '.zip'), contnerFileName)

    @staticmethod
    def manageSubtileFile(fileData, fileName, contnerFileName):
        #TODO: rename file to match the content !
        with open(fileName, "wb") as subFile:
            subFile.write(fileData)
        subFile.close()

        with open(fileName, 'rb') as subtitleFile:
            subZip = zipfile.ZipFile(subtitleFile)
            for name in subZip.namelist():
                if name.endswith('.srt'):
                    subZip.extract(name, os.path.split(fileName)[0])

    @staticmethod
    def classFactory(class_name):
        class_lower_name = class_name.lower()

        if class_name in SUBTITLE_SITE_LIST:
            engines_path = os.path.dirname(__file__)
            if engines_path not in sys_path:
                sys_path.insert(0, engines_path)

            subtitle_module = import_module(class_lower_name)
            subtitle_class = getattr(subtitle_module, class_name)

            return subtitle_class()
