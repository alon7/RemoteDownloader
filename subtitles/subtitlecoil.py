# -*- coding: utf-8 -*-
from subtitles.subtitlesite import SubtitleSite
from utils import Utils
from itertools import groupby


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


class SubtitleCoIl(SubtitleSite):
    def __init__(self):
        super(self.__class__, self).__init__(SUBTITLE_PAGES.DOMAIN)
        self.configuration_name = "subtitlescoil"
        self._is_logged_in(SUBTITLE_PAGES.DOMAIN + "/")

    @staticmethod
    @Utils.timefunc
    def isSeries(search_content):
        return bool(Utils.getregexresults(SUBTITLE_REGEX.TV_SERIES_RESULTS_PARSER, search_content))

    @staticmethod
    @Utils.timefunc
    def getVersionsList(page_content):
        results = Utils.getregexresults(SUBTITLE_REGEX.SUBTITLE_LIST_PARSER, page_content, True)
        for result in results:
            result['DownloadPage'] = SUBTITLE_PAGES.DOWNLOAD % result['VerCode']
            result['Domain'] = SUBTITLE_PAGES.DOMAIN
            result.pop('VerCode', None)
            result.pop('Language', None)  #?
        return results

    @Utils.timefunc
    def getSeasonsList(self, series_code):
        series_page = self.urlHandler.request(SUBTITLE_PAGES.DOMAIN,
                                              SUBTITLE_PAGES.SERIES_SUBTITLES % series_code)
        total_seasons = Utils.getregexresults(SUBTITLE_REGEX.TV_SEASON_PATTERN, series_page, True)
        return total_seasons

    @Utils.timefunc
    def getEpisodesList(self, series_code, season_code):
        season_page = self.urlHandler.request(SUBTITLE_PAGES.DOMAIN,
                                              SUBTITLE_PAGES.SERIES_SEASON % (series_code, season_code))
        total_episodes = Utils.getregexresults(SUBTITLE_REGEX.TV_EPISODE_PATTERN, season_page, True)
        return total_episodes

    @Utils.timefunc
    def findSubtitles(self, contentToDownload):
        contentName = contentToDownload.title
        searchResults = []

        resulstPage = self.urlHandler.request(
            SUBTITLE_PAGES.DOMAIN,
            SUBTITLE_PAGES.SEARCH % contentName.replace(' ', '+'))

        moviesInfo = list(   map(lambda r: {'content': r, 'type': 'movie'},
                                Utils.getregexresults(SUBTITLE_REGEX.MOVIE_RESULTS_PARSER,
                                resulstPage, True)))

        #If we got series in the result, extract it too
        if SubtitleCoIl.isSeries(resulstPage):
            for series in Utils.getregexresults(SUBTITLE_REGEX.TV_SERIES_RESULTS_PARSER, resulstPage, True):
                moviesInfo.append({'content': series, 'type': 'series'})


        for type, results in groupby(moviesInfo, lambda i: i['type']):
            if 'movie' == contentToDownload.movieOrSeries == type:
                for result in results:
                    moviecode = result['content']['MovieCode']
                    moviename = result['content']['MovieName']

                    page_content = self.urlHandler.request(
                        SUBTITLE_PAGES.DOMAIN,
                        SUBTITLE_PAGES.MOVIE_SUBTITLES % moviecode)
                    allVersions = SubtitleCoIl.getVersionsList(page_content)
                    if None != contentToDownload.torrents:
                        for versionDict in allVersions:
                            for torrent in contentToDownload.torrents:
                                if Utils.versionMatching(torrent.get('name'), versionDict.get('VerSum')):
                                    searchResults.extend((torrent, versionDict))
                    else:
                        searchResults.extend(allVersions)
            elif 'series' == contentToDownload.movieOrSeries == type:
                for result in results:
                    seriescode = result['content']['MovieCode']
                    seriesname = result['content']['MovieName']
                    total_seasons = self.getSeasonsList(seriescode)

                    #Iterate through all relevant seasons
                    for season in total_seasons:
                            seasoncode = season['SeasonCode']
                            seasonnum = season['SeasonNum']

                            if seasonnum == contentToDownload.season or contentToDownload.wholeSeriesFlag:
                                total_episodes = self.getEpisodesList(seriescode, seasoncode)
                                for episode in total_episodes:
                                    if episode['EpisodeNum'] == contentToDownload.episodeNumber or contentToDownload.wholeSeasonFlag or contentToDownload.wholeSeriesFlag:
                                        episodeVersions = self.urlHandler.request(SUBTITLE_PAGES.DOMAIN,
                                                                                  SUBTITLE_PAGES.SERIES_EPISODE % (seriescode, seasoncode, episode['EpisodeCode']))
                                        allVersions = SubtitleCoIl.getVersionsList(episodeVersions)
                                        if None != contentToDownload.torrents:
                                            for versionDict in allVersions:
                                                for torrent in contentToDownload.torrents:
                                                    if Utils.versionMatching(torrent.get('name'), versionDict.get('VerSum')):
                                                        searchResults.extend((torrent, versionDict))
                                        else:
                                            searchResults.extend(allVersions)

        return searchResults

    @Utils.timefunc
    def _is_logged_in(self, url):
        data = self.urlHandler.request(self.domain, url)
        if data is not None and Utils.getregexresults(SUBTITLE_REGEX.SUCCESSFUL_LOGIN, data):
            return data
        elif self.login():
            return self.urlHandler.request(self.domain, url)
        else:
            return None

    @Utils.timefunc
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

if __name__ == "__main__":
    #c = content.Content("blue jasmin", "movie")
    sc = SubtitleCoIl()
    #g = sc.findSubtitles(c)
    sc.download_subtitle('260628', "Blue.Jasmine.2013.720p.BluRay.x264-SPARKS.zip")
    print 4
