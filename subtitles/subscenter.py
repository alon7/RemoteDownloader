import subtitles.subtitle
import json
import re
import content
import Utils


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
        r'\<a href\=\"http\:\/\/subscenter.cinemast.com\/he\/subtitle\/' \
        '(?P<Type>movie|series)\/(?P<Code>[A-Za-z0-9\-]*?)\/\">' \
        '(?P<MovieName>[^>]*?)</a>'
    SERIES_VAR = r'var episodes_group = (.*?}}})'
    LOGIN_VALIDATION = r"name='csrfmiddlewaretoken' value='(.*?)'"


def getJson(rawJson):
    def asciirepl(match):
        return '\\u00' + match.group()[2:]

    p = re.compile(r'\\x(\w{2})')
    rawJson = p.sub(asciirepl, rawJson)
    return json.loads(rawJson)


class Subcenter(subtitles.subtitle.Subtitle):
    BLACK_LIST_QUALITIES = [u'ALL']

    def __init__(self):
        super(self.__class__, self).__init__(SUBSCENTER_PAGES.DOMAIN)
        self.configuration_name = "subcenter"

    @staticmethod
    def getVersionsList(versionsJson):
        """
            This function will get the versions page of the movie/series and
            return a tuple of vesrions summary and a formatted dictionary where
            each key is the version_sum and the values are movie_code,
            version_code and downloads count.
        """
        allVersions = {}

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

                            if not allVersions.get(verSum):
                                allVersions[verSum] = {
                                    "movie_code": version['id'],
                                    "version_code": version['key']}

        return allVersions

    @staticmethod
    def getEpisodesList(series_area_content):
        """
            This function will get the series page, and return all the episodes
            inside this page return value will be List<season_id, episode_id>.
        """
        all_episodes = []
        jsoned_series_page_dict = getJson(series_area_content[0])
        total_seasons = jsoned_series_page_dict.keys()

        for season in total_seasons:
            total_episodes = jsoned_series_page_dict[season].keys()
            for episode in total_episodes:
                all_episodes.append({'season_id': jsoned_series_page_dict[season][episode]['season_id'],
                                     'episode_id': jsoned_series_page_dict[season][episode]['episode_id']})
        return all_episodes

    def _getMovieSubStageForMovie(self, movieName, movieCode):
        versionsJson = self.urlHandler.request(
            SUBSCENTER_PAGES.DOMAIN,
            SUBSCENTER_PAGES.MOVIE_JSON % movieCode)

        all_versions = self.getVersionsList(versionsJson)

        return (
            movieName,
            movieCode,
            'movie',
            all_versions)

    def _getMovieSubStagesForSeries(self, series_name, movie_code):
        series_page = self.urlHandler.request(
            SUBSCENTER_PAGES.DOMAIN,
            SUBSCENTER_PAGES.SERIES % movie_code)
        series_area_content = Utils.getregexresults(
            SUBSCENTER_REGEX.SERIES_VAR,
            series_page)
        all_episodes = \
            Subcenter.getEpisodesList(series_area_content)

        # Default version summary for series (otherwise we'll have to
        # query all the avaliable episodes pages
        default_versum = 'Sub types are not supported in this provider'

        for episode in all_episodes:
            # json returns the ids as number, so conversion to str is
            # needed.
            season_id = str(episode['season_id'])
            episode_id = str(episode['episode_id'])
            # We put fomratted version of the episode in order to match
            # the file name format. for example:
            # The.Big.Bang.Theory.S05E16.720p.HDTV.X264-DIMENSION
            # The rjust function is used in order to create 2 digit
            # wide number.
            fotmatted_episode = 'S%sE%s' % \
                                (season_id.rjust(2, '0'), episode_id.rjust(2, '0'))
            yield (
                '%s %s' % (series_name, fotmatted_episode),
                '%s/%s/%s' % (movie_code, season_id, episode_id),
                default_versum,
                {'type': 'series'})

    def findSubtitles(self, contentToDownload):
        movieNameFromContent = contentToDownload.title
        searchResults = []

        resultsPage = self.urlHandler.request(
            SUBSCENTER_PAGES.DOMAIN,
            SUBSCENTER_PAGES.SEARCH % movieNameFromContent.replace(' ', '+'))

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
                searchResults.append(self._getMovieSubStageForMovie(movieNameInEnglish, movieCode))

            elif movieType == 'series' == contentToDownload.movieOrSeries:
                for stage in self._getMovieSubStagesForSeries(movieNameInEnglish, movieCode):
                    searchResults.append(stage)

        return searchResults

    def findVersionSubStageList(self, movie_sub_stage):

        # A dictionary where keys are the version_sum and the values are dicts
        # with movie_code and version_code.

        # If it's a movie, the results are already inside the extra param.
        if movie_sub_stage.extra['type'] == 'movie':
            all_versions = movie_sub_stage.extra['all_versions']
        # Else, on series, we still got work to do
        else:
            series_code = movie_sub_stage.movie_code

            versions_json = self.urlHandler.request(
                SUBSCENTER_PAGES.DOMAIN,
                SUBSCENTER_PAGES.SERIES_JSON % tuple(series_code.split("/")))
            (ver_sum, all_versions) = \
                Subcenter.getVersionsList(versions_json)

        version_sub_stages = []
        for version_sum, item in all_versions.iteritems():
            version_sub_stages.append(
                version_sum,
                item['version_code'],
                item['movie_code'])

        return version_sub_stages

    def download_subtitle(self, version_sum, version_code, movie_code, filename):
        download_page = SUBSCENTER_PAGES.DOWN_PAGE % (
            SUBSCENTER_LANGUAGES.HEBREW,
            movie_code,
            # Replace spaces with their code
            version_sum.replace(' ', '%20'),
            version_code)

        f = self.urlHandler.request(self.domain, download_page)
        with open(filename, "wb") as subFile:
            subFile.write(f)
        subFile.close()


if __name__ == "__main__":
    c = content.Content("Breaking Bad", "series")
    sc = Subcenter()
    g = sc.findSubtitles(c)
    #sc.download_subtitle('12.Years.a.Slave.[2013].1080p.BluRay.AAC.x264-tomcat12', 'f1babe584f0d8509e99cc3e4a82f43cb', "267473", "NOWAY!!.zip")
    print 4