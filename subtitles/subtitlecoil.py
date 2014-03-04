# -*- coding: utf-8 -*-

import subtitles.subtitle
import re
import urllib
import Utils


class SUBTITLE_PAGES:
    DOMAIN = 'http://www.subtitle.co.il'
    SEARCH = '/browse.php?q=%s'
    MOVIE_SUBTITLES = '/view.php?id=%s&m=subtitles'
    SERIES_SUBTITLES = '/viewseries.php?id=%s&m=subtitles#'
    SERIES_SEASON = '/viewseries.php?id=%s&m=subtitles&s=%s'  # SeriesId & SeasonId
    SERIES_EPISODE = '/viewseries.php?id=%s&m=subtitles&s=%s&e=%s'  # SeriesId & SeasonId & EpisodeId
    DOWNLOAD = '/downloadsubtitle.php?id=%s'
    LOGIN = '/login.php'
    LANGUAGE = None



class SUBTITLE_REGEX:
    TV_SERIES_RESULTS_PARSER = '<div class=\"browse_title_name\" itemprop=\"name\"><a href=\"viewseries.php\?id=(?P<MovieCode>\d+).*?class=\"smtext">(?P<MovieName>.*?)</div>'
    TV_SEASON_PATTERN = 'seasonlink_(?P<SeasonCode>\d+).*?>(?P<SeasonNum>\d+)</a>'
    TV_EPISODE_PATTERN = 'episodelink_(?P<EpisodeCode>\d+).*?>(?P<EpisodeNum>\d+)</a>'
    MOVIE_RESULTS_PARSER = '<div class=\"browse_title_name\" itemprop=\"name\"><a href=\"view.php\?id=(?P<MovieCode>\d+).*?class=\"smtext">(?P<MovieName>.*?)</div>'
    SUBTITLE_LIST_PARSER = 'downloadsubtitle\.php\?id=(?P<VerCode>\d*).*?subt_lang.*?title=\"(?P<Language>.*?)\".*?subtitle_title.*?title=\"(?P<VerSum>.*?)\"'
    VER_SUM_PARSER = '<td class=\"FamilySubtitlesVerisons\"><a name="f\d"></a>(.*?)</td>'
    FAILED_LOGIN = r'<form action="/login\.php"'
    SUCCESSFUL_LOGIN = r'friends\.php'


class SubtitleCoIl(subtitles.subtitle.Subtitle):
    def __init__(self):
        super(self.__class__, self).__init__(SUBTITLE_PAGES.DOMAIN)
        self.configuration_name = "subtitlescoil"

    @staticmethod
    def isSeries(search_content):
        return bool(Utils.getregexresults(SUBTITLE_REGEX.TV_SERIES_RESULTS_PARSER, search_content))

    @staticmethod
    def getVersionsList(page_content):
        results = Utils.getregexresults(SUBTITLE_REGEX.SUBTITLE_LIST_PARSER, page_content, True)
        return results

    def getSeasonsList(self, series_code):
        series_page = self.urlHandler.request( SUBTITLE_PAGES.DOMAIN,
                                               SUBTITLE_PAGES.SERIES_SUBTITLES % series_code)
        total_seasons = Utils.getregexresults(SUBTITLE_REGEX.TV_SEASON_PATTERN, series_page, True)
        return total_seasons

    def getEpisodesList(self, series_code, season_code):
        season_page = self.urlHandler.request( SUBTITLE_PAGES.DOMAIN,
                                               SUBTITLE_PAGES.SERIES_SEASON % (series_code, season_code))
        total_episodes = Utils.getregexresults(SUBTITLE_REGEX.TV_EPISODE_PATTERN, season_page, True)
        return total_episodes

    def download_subtitle(self, id, filename):
        url = SUBTITLE_PAGES.DOWNLOAD % id
        f = self.urlHandler.request(self.domain, url)

        with open(filename, "wb") as subFile:
            subFile.write(f)
        subFile.close()

    def _is_logged_in(self, url):
        content = self.urlHandler.request(self.domain, url)
        if content is not None and Utils.getregexresults(SUBTITLE_REGEX.SUCCESSFUL_LOGIN, content):
            return content
        elif self.login():
            return self.urlHandler.request(self.domain, url)
        else:
            return None

    def login(self):
        email = self.configuration.get(self.configuration_name, "email")
        password = self.configuration.get(self.configuration_name, "password")
        query = {'email': email, 'password': password, 'Login': 'התחבר'}
        content = self.urlHandler.request(self.domain, SUBTITLE_PAGES.LOGIN, query)
        if Utils.getregexresults(SUBTITLE_REGEX.FAILED_LOGIN, content):
            return None
        else:
            self.urlHandler.save_cookie()
            return True
