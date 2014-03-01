# -*- coding: utf-8 -*-

import re
import urllib
from subtitles.urlHandler import URLHandler
import ConfigParser
import io

# TODO: unzip subtitles zip files


class SubtitleCoIl():

    CONFIG = ConfigParser.RawConfigParser()
    CONFIG.readfp(open('..\configuration\subtitlesConfig.cfg'))

    BASE_URL = "http://www.subtitle.co.il"

    def __init__(self):
        self.urlHandler = URLHandler()

    def get_subtitle_list(self, item):
        if item["tvshow"]:
            search_results = self._search_tvshow(item)
            results = self._build_tvshow_subtitle_list(search_results, item)
        else:
            search_results = self._search_movie(item)
            results = self._build_movie_subtitle_list(search_results, item)

        return results

    # return list of tv-series from the site`s search
    def _search_tvshow(self, item):
        search_string = re.split(r'\s\(\w+\)$', item["tvshow"])[0]

        results = None

        if not results:
            query = {"q": search_string.lower(), "cs": "series"}

            search_result = self.urlHandler.request(self.BASE_URL + "/browse.php?" + urllib.urlencode(query))
            if search_result is None:
                return results  # return empty set

            urls = re.findall(
                u'<a href="viewseries\.php\?id=(\d+)[^"]+" itemprop="url">[^<]+</a></div><div style="direction:ltr;" class="smtext">([^<]+)</div>',
                search_result)

            results = self._filter_urls(urls, search_string, item)
        else:
            results = eval(results)

        return results

    # return list of movie from the site`s search
    def _search_movie(self, item):
        results = []
        search_string = item["title"]
        query = {"q": search_string.lower(), "cs": "movies"}
        if item["year"]:
            query["fy"] = int(item["year"]) - 1
            query["uy"] = int(item["year"]) + 1

        search_result = self.urlHandler.request(self.BASE_URL + "/browse.php?" + urllib.urlencode(query))
        if search_result is None:
            return results  # return empty set

        urls = re.findall(
            u'<a href="view\.php\?id=(\d+)[^"]+" itemprop="url">[^<]+</a></div><div style="direction:ltr;" class="smtext">([^<]+)</div><span class="smtext">(\d{4})</span>',
            search_result)

        results = self._filter_urls(urls, search_string, item)
        return results

    def _filter_urls(self, urls, search_string, item):
        filtered = []
        search_string = search_string.lower()

        if not item["tvshow"]:
            for (id, eng_name, year) in urls:
                if search_string.startswith(eng_name.lower()) and \
                        (item["year"] == '' or
                                 year == '' or
                                     (int(year) - 1) <= int(item["year"]) <= (int(year) + 1) or
                                     (int(item["year"]) - 1) <= int(year) <= (int(item["year"]) + 1)):
                    filtered.append({"name": eng_name, "id": id, "year": year})
        else:
            for (id, eng_name) in urls:
                if search_string.startswith(eng_name.lower()):
                    filtered.append({"name": eng_name, "id": id})

        return filtered

    def _build_movie_subtitle_list(self, search_results, item):
        ret = []
        total_downloads = 0
        for result in search_results:
            url = self.BASE_URL + "/view.php?" + urllib.urlencode({"id": result["id"], "m": "subtitles"})
            subtitle_page = self._is_logged_in(url)
            x, i = self._retrive_subtitles(subtitle_page, item)
            total_downloads += i
            ret += x

        # Fix the rating
        if total_downloads:
            for it in ret:
                it["rating"] = str(int(round(it["rating"] / float(total_downloads), 1) * 5))

        return sorted(ret, key=lambda x: (x['lang_index'], x['sync'], x['rating']), reverse=True)

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

    def download(self, id, zip_filename):
        query = {"id": id}
        url = self.BASE_URL + "/downloadsubtitle.php?" + urllib.urlencode(query)
        f = self.urlHandler.request(url)

        with open(zip_filename, "wb") as subFile:
            subFile.write(f)
        subFile.close()

    def _is_logged_in(self, url):
        content = self.urlHandler.request(url)
        if content is not None and re.search(r'friends\.php', content):  #  check if logged in
            return content
        elif self.login():
            return self.urlHandler.request(url)
        else:
            return None

    def login(self):
        #  TODO: get data from configuration file!
        email = self.CONFIG.get("subtitlescoil", "email")
        password = self.CONFIG.get("subtitlescoil","password")
        query = {'email': email, 'password': password, 'Login': 'התחבר'}
        content = self.urlHandler.request(self.BASE_URL + "/login.php", query)
        if re.search(r'<form action="/login\.php"', content):
            return None
        else:
            self.urlHandler.save_cookie()
            return True