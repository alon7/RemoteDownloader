import json
import re
from subtitles.subtitlesite import SubtitleSite
from utils import Utils


class SUBSCENTER_LANGUAGES:
    ENGLISH = u'en'
    HEBREW = u'he'


class SUBSCENTER_PAGES:
    DOMAIN = r'http://subscenter.cinemast.com'
    SEARCH = r'/he/subtitle/search/?q=%s'
    MOVIE_JSON = r'/he/cinemast/data/movie/sb/%s/'
    SERIES = r'/he/subtitle/series/%s/'
    SERIES_JSON = r'/he/cinemast/data/series/sb/%s/%s/%s/'  # series, season, episode
    DOWN_PAGE = r'/subtitle/download/%s/%s/?v=%s&key=%s'  # lang, code, version, key
    LOGIN = '/he/subscenter/accounts/login/'
    LANGUAGE = None


class SUBSCENTER_REGEX:
    SEARCH_RESULTS_PARSER = \
        r'\<a href\=\"http\:\/\/(subscenter|www).cinemast.com\/he\/(subtitle|cinemast)\/' \
        '(?P<Type>movie|series)\/(?P<Code>[A-Za-z0-9\-]*?)\/\">' \
        '(?P<MovieName>[^>]*?)</a>'
    SERIES_VAR = r'var episodes_group = (.*?}}})'


def getJson(rawJson):
    def asciirepl(match):
        return '\\u00' + match.group()[2:]

    p = re.compile(r'\\x(\w{2})')
    rawJson = p.sub(asciirepl, rawJson)
    return json.loads(rawJson)


class SubsCenter(SubtitleSite):
    BLACK_LIST_QUALITIES = [u'ALL']

    def __init__(self):
        super(self.__class__, self).__init__(SUBSCENTER_PAGES.DOMAIN)
        self.configuration_name = "subcenter"

    @staticmethod
    @Utils.timefunc
    def getVersionsList(versionsJson):
        #TODO: FIX THIS... a lot of Unnecessary things!
        """
            This function will get the versions page of the movie/series and
            return a tuple of vesrions summary and a formatted dictionary where
            each key is the versionSum and the values are movieCode,
            versionCode and downloads count.
        """
        allVersions = []

        jsonedMoviePageDict = getJson(versionsJson)
        currentLanguageProviders = jsonedMoviePageDict.get(SUBSCENTER_LANGUAGES.HEBREW)

        totalQualities = []

        if currentLanguageProviders:
            for qualities in currentLanguageProviders.values():
                for quality, versions in qualities.iteritems():
                    if quality not in SubsCenter.BLACK_LIST_QUALITIES and quality not in totalQualities:
                        totalQualities.append(quality)

                        for version in versions.values():
                            verSum = version['subtitle_version']
                            allVersions.append({
                                "VerSum": verSum,
                                'Domain': SUBSCENTER_PAGES.DOMAIN,
                                'DownloadPage': SUBSCENTER_PAGES.DOWN_PAGE % (SUBSCENTER_LANGUAGES.HEBREW,
                                                                              version['id'],
                                                                              verSum.replace(' ', '%20'),
                                                                              version['key'])})

        return allVersions

    @staticmethod
    @Utils.timefunc
    def getEpisodesList(seriesAreaContent):
        """
            This function will get the series page, and return all the episodes
            inside this page return value will be List<seasonId, episodeId>.
        """
        allEpisodes = []
        jsonedSeriesPageDict = getJson(seriesAreaContent[0])
        totalSeasons = jsonedSeriesPageDict.keys()

        for season in totalSeasons:
            totalEpisodes = jsonedSeriesPageDict[season].keys()
            for episode in totalEpisodes:
                allEpisodes.append({'seasonId': jsonedSeriesPageDict[season][episode]['season_id'],
                                    'episodeId': jsonedSeriesPageDict[season][episode]['episode_id']})
        return allEpisodes

    @Utils.timefunc
    def getMovieVersions(self, movieCode):
        versionsJson = self.urlHandler.request(
            SUBSCENTER_PAGES.DOMAIN,
            SUBSCENTER_PAGES.MOVIE_JSON % movieCode)

        allVersions = self.getVersionsList(versionsJson)
        return allVersions

    @Utils.timefunc
    def getEpisodeVersions(self, episdoe):
        seriesCode = episdoe.get('seriesCode')
        versionsJson = self.urlHandler.request(
            SUBSCENTER_PAGES.DOMAIN,
            SUBSCENTER_PAGES.SERIES_JSON % tuple(seriesCode.split("/")))
        allVersions = SubsCenter.getVersionsList(versionsJson)
        return allVersions

    @Utils.timefunc
    def getEpisodes(self, seriesName, movieCode):
        seriesPage = self.urlHandler.request(
            SUBSCENTER_PAGES.DOMAIN,
            SUBSCENTER_PAGES.SERIES % movieCode)
        seriesAreaContent = Utils.getregexresults(
            SUBSCENTER_REGEX.SERIES_VAR,
            seriesPage)
        allEpisodes = \
            SubsCenter.getEpisodesList(seriesAreaContent)

        for episode in allEpisodes:
            seasonId = str(episode['seasonId'])
            episodeId = str(episode['episodeId'])
            fotmatted_episode = 'S%sE%s' % \
                                (seasonId.rjust(2, '0'), episodeId.rjust(2, '0'))
            yield {'prettyName': '%s %s' % (seriesName, fotmatted_episode),
                   'seriesCode': '%s/%s/%s' % (movieCode, seasonId, episodeId),
                   'season': seasonId,
                   'episode': episodeId,
                   'type': 'series'}

    @Utils.timefunc
    def findSubtitles(self, contentToDownload):
        contentName = contentToDownload.title
        searchResults = []

        resultsPage = self.urlHandler.request(
            SUBSCENTER_PAGES.DOMAIN,
            SUBSCENTER_PAGES.SEARCH % contentName.replace(' ', '+'))

        moviesInfo = Utils.getregexresults(
            SUBSCENTER_REGEX.SEARCH_RESULTS_PARSER, resultsPage, True)

        for movieInfo in moviesInfo:
            movieCode = movieInfo['Code']
            movieType = movieInfo['Type']
            movieName = movieInfo['MovieName']

            try:
                movieNameInEnglish = movieName.split(' / ')[1]
            except ValueError:
                movieNameInEnglish = movieName

            if movieType == 'movie' == contentToDownload.movieOrSeries:
                allVersions = self.getMovieVersions(movieNameInEnglish)
                if None != contentToDownload.torrents:
                    for versionDict in allVersions:
                        for torrent in contentToDownload.torrents:
                            if Utils.versionMatching(torrent.get('name'), versionDict.get('VerSum')):
                                searchResults.extend((torrent, versionDict))
                else:
                    searchResults.extend(allVersions)

            elif movieType == 'series' == contentToDownload.movieOrSeries:
                for episode in self.getEpisodes(movieNameInEnglish, movieCode):
                    if (episode.get('season') == contentToDownload.season and episode.get(
                            'episode') == contentToDownload.episodeNumber) or (episode.get(
                            'season') == contentToDownload.season and contentToDownload.wholeSeasonFlag) or contentToDownload.wholeSeriesFlag:
                        allVersions = self.getEpisodeVersions(episode)
                        if None != contentToDownload.torrents:
                            for versionDict in allVersions:
                                for torrent in contentToDownload.torrents:
                                    if Utils.versionMatching(torrent.get('name'), versionDict.get('VerSum')):
                                        searchResults.extend((torrent, versionDict))

                        else:
                            searchResults.extend(allVersions)

        return searchResults