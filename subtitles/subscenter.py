import json
import re
import content
from subtitles.subtitle import Subtitle
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


class Subcenter(Subtitle):
    BLACK_LIST_QUALITIES = [u'ALL']

    def __init__(self):
        super(self.__class__, self).__init__(SUBSCENTER_PAGES.DOMAIN)
        self.configuration_name = "subcenter"

    @staticmethod
    def getVersionsList(versionsJson):
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
                    if quality not in Subcenter.BLACK_LIST_QUALITIES and quality not in totalQualities:
                        totalQualities.append(quality)

                        for version in versions.values():
                            verSum = version['subtitle_version']
                            allVersions.append({
                                "verSum": verSum,
                                "movieCode": version['id'],
                                "VerCode": version['key']})

        return allVersions

    @staticmethod
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

    def getMovieVersions(self, movieName, movieCode):
        versionsJson = self.urlHandler.request(
            SUBSCENTER_PAGES.DOMAIN,
            SUBSCENTER_PAGES.MOVIE_JSON % movieCode)

        allVersions = self.getVersionsList(versionsJson)

        return (
            movieName,
            allVersions)

    def getEpisodeVersions(self, episdoe):
        seriesCode = episdoe[1]
        versionsJson = self.urlHandler.request(
            SUBSCENTER_PAGES.DOMAIN,
            SUBSCENTER_PAGES.SERIES_JSON % tuple(seriesCode.split("/")))
        allVersions = Subcenter.getVersionsList(versionsJson)
        return allVersions

    def getEpisodes(self, seriesName, movieCode):
        seriesPage = self.urlHandler.request(
            SUBSCENTER_PAGES.DOMAIN,
            SUBSCENTER_PAGES.SERIES % movieCode)
        seriesAreaContent = Utils.getregexresults(
            SUBSCENTER_REGEX.SERIES_VAR,
            seriesPage)
        allEpisodes = \
            Subcenter.getEpisodesList(seriesAreaContent)

        # Default version summary for series (otherwise we'll have to
        # query all the avaliable episodes pages

        for episode in allEpisodes:
            # json returns the ids as number, so conversion to str is
            # needed.
            seasonId = str(episode['seasonId'])
            episodeId = str(episode['episodeId'])
            # We put fomratted version of the episode in order to match
            # the file name format. for example:
            # The.Big.Bang.Theory.S05E16.720p.HDTV.X264-DIMENSION
            # The rjust function is used in order to create 2 digit
            # wide number.
            fotmatted_episode = 'S%sE%s' % \
                                (seasonId.rjust(2, '0'), episodeId.rjust(2, '0'))
            yield (
                '%s %s' % (seriesName, fotmatted_episode),
                '%s/%s/%s' % (movieCode, seasonId, episodeId),
                {'type': 'series'})

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
                searchResults.append(self.getMovieVersions(movieNameInEnglish, movieCode))

            elif movieType == 'series' == contentToDownload.movieOrSeries:
                #TODO: choose only desired episodes
                for episdoe in self.getEpisodes(movieNameInEnglish, movieCode):
                    searchResults.append((movieNameInEnglish, self.getEpisodeVersions(episdoe)))

        return searchResults

    def downloadSubtitle(self, versionSum, versionCode, movieCode, filename):
        downloadPage = SUBSCENTER_PAGES.DOWN_PAGE % (
            SUBSCENTER_LANGUAGES.HEBREW,
            movieCode,
            # Replace spaces with their code
            versionSum.replace(' ', '%20'),
            versionCode)

        fileData = self.urlHandler.request(self.domain, downloadPage)
        self.manageSubtileFile(fileData, "ShouldCreateABetterFileName.zip")

if __name__ == "__main__":
    c = content.Content("breaking bad", "series")
    sc = Subcenter()
    g = sc.findSubtitles(c)
    #sc.download_subtitle('12.Years.a.Slave.[2013].1080p.BluRay.AAC.x264-tomcat12', 'f1babe584f0d8509e99cc3e4a82f43cb', "267473", "NOWAY!!.zip")
    print 4