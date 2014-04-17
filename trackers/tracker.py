from os import path
from sys import exit, path as sys_path
from importlib import import_module
from abc import ABCMeta

TRACKER_SITE_LIST = ['ThePirateBay', 'PublicHD', 'KickAssTorrents']


class TrackerSite(object):
    __metaclass__ = ABCMeta


    @staticmethod
    def classFactory(class_name):
        class_lower_name = class_name.lower()

        if class_name in TRACKER_SITE_LIST:
            engines_path = path.dirname(__file__)
            if engines_path not in sys_path:
                sys_path.insert(0, engines_path)

            subtitle_module = import_module(class_lower_name)
            subtitle_class = getattr(subtitle_module, class_name)

            return subtitle_class()