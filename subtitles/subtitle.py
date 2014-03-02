# -*- coding: utf-8 -*-

import re
import urllib
from subtitles.urlHandler import URLHandler
import ConfigParser
from abc import abstractmethod, ABCMeta

# TODO: unzip subtitles zip files


class Subtitle(object):
    __metaclass__ = ABCMeta

    def __init__(self, base_url):
        super(Subtitle, self).__init__()
        self.base_url = base_url
        self.urlHandler = URLHandler()
        self.configuration = ConfigParser.RawConfigParser()
        self.configuration.readfp(open('..\configuration\subtitlesConfig.cfg'))

    @abstractmethod
    def get_subtitle_list(self, item):
        pass

    # return list of tv-series from the site`s search
    @abstractmethod
    def _search_tvshow(self, item):
        pass

    # return list of movie from the site`s search
    @abstractmethod
    def _search_movie(self, item):
        pass

    @abstractmethod
    def _filter_urls(self, urls, search_string, item):
        pass

    @abstractmethod
    def _build_movie_subtitle_list(self, search_results, item):
        pass

    @abstractmethod
    def download_subtitle(self, id, zip_filename):
        pass

    @abstractmethod
    def _is_logged_in(self, url):
        pass

    @abstractmethod
    def login(self):
        pass


"""
    # def _build_tvshow_subtitle_list(self, search_results, item):
    #     ret = []
    #     total_downloads = 0
    #
    #     for result in search_results:
    #         cache_key_season = get_cache_key("tv-show", "%s_%s" % (result["name"], "seasons"))
    #         subtitle_page = cache.get(cache_key_season)
    #         if not subtitle_page:
    #             used_cached_seasons = False
    #             url = self.BASE_URL + "/viewseries.php?" + urllib.urlencode({"id": result["id"], "m": "subtitles"})
    #             subtitle_page = self._is_logged_in(url)
    #             if subtitle_page is not None:
    #                 # Retrieve the requested season
    #                 subtitle_page = re.findall("seasonlink_(\d+)[^>]+>(\d+)</a>", subtitle_page)
    #                 if subtitle_page:
    #                     cache.set(cache_key_season, repr(subtitle_page))
    #         else:
    #             used_cached_seasons = True
    #             subtitle_page = eval(subtitle_page)
    #
    #         if subtitle_page:
    #             season_found = False
    #             for (season_id, season_num) in subtitle_page:
    #                 if season_num == item["season"]:
    #                     season_found = True
    #
    #                     cache_key_episode = get_cache_key("tv-show",
    #                                                       "%s_s%s_%s" % (result["name"], season_num, "episodes"))
    #                     found_episodes = cache.get(cache_key_episode)
    #                     if not found_episodes:
    #                         used_cached_episodes = False
    #                         # Retrieve the requested episode
    #                         url = self.BASE_URL + "/getajax.php?" + urllib.urlencode({"seasonid": season_id})
    #                         subtitle_page = self.urlHandler.request(url)
    #                         if subtitle_page is not None:
    #                             found_episodes = re.findall("episodelink_(\d+)[^>]+>(\d+)</a>", subtitle_page)
    #
    #                             if found_episodes:
    #                                 cache.set(cache_key_episode, repr(found_episodes))
    #                     else:
    #                         used_cached_episodes = True
    #                         found_episodes = eval(found_episodes)
    #
    #                     if found_episodes:
    #                         episode_found = False
    #                         for (episode_id, episode_num) in found_episodes:
    #                             if episode_num == item["episode"]:
    #                                 episode_found = True
    #
    #                                 url = self.BASE_URL + "/getajax.php?" + urllib.urlencode(
    #                                     {"episodedetails": episode_id})
    #                                 subtitle_page = self.urlHandler.request(url)
    #
    #                                 x, i = self._retrive_subtitles(subtitle_page, item)
    #                                 total_downloads += i
    #                                 ret += x
    #
    #                         if not episode_found and used_cached_episodes:
    #                             cache.delete(cache_key_episode)  # used cached episodes list and not found
    #                             return self._build_tvshow_subtitle_list(search_results, item)  # try the search again
    #
    #             if not season_found and used_cached_seasons:
    #                 cache.delete(cache_key_season)  # used cached season list and not found so delete the cache
    #                 return self._build_tvshow_subtitle_list(search_results, item)  # try the search again
    #
    #     # Fix the rating
    #     if total_downloads:
    #         for it in ret:
    #             it["rating"] = str(int(round(it["rating"] / float(total_downloads), 1) * 5))
    #
    #     return sorted(ret, key=lambda x: (x['lang_index'], x['sync'], x['rating']), reverse=True)

    # def _retrive_subtitles(self, page, item):
    #     ret = []
    #     total_downloads = 0
    #     if page is not None:
    #         found_subtitles = re.findall(
    #             "downloadsubtitle\.php\?id=(?P<fid>\d*).*?subt_lang.*?title=\"(?P<language>.*?)\".*?subtitle_title.*?title=\"(?P<title>.*?)\">.*?>(?P<downloads>[^ ]+) הורדות",
    #             page)
    #         for (subtitle_id, language, title, downloads) in found_subtitles:
    #             if xbmc.convertLanguage(heb_to_eng(language), xbmc.ISO_639_2) in item["3let_language"]:
    #                 subtitle_rate = self._calc_rating(title, item["file_original_path"])
    #                 total_downloads += int(downloads.replace(",", ""))
    #                 ret.append(
    #                     {'lang_index': item["3let_language"].index(
    #                         xbmc.convertLanguage(heb_to_eng(language), xbmc.ISO_639_2)),
    #                      'filename': title,
    #                      'link': subtitle_id,
    #                      'language_name': xbmc.convertLanguage(heb_to_eng(language),
    #                                                            xbmc.ENGLISH_NAME),
    #                      'language_flag': xbmc.convertLanguage(heb_to_eng(language),
    #                                                            xbmc.ISO_639_1),
    #                      'ID': subtitle_id,
    #                      'rating': int(downloads.replace(",", "")),
    #                      'sync': subtitle_rate >= 4,
    #                      'hearing_imp': 0
    #                     })
    #     return ret, total_downloads
    """
