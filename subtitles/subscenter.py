import subtitles.subtitle
import json
import re
import content
import Utils


class SUBSCENTER_LANGUAGES:
    ENGLISH = 'en'
    HEBREW = 'he'


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


def getJson(content):
    def asciirepl(match):
        return '\\u00' + match.group()[2:]

    p = re.compile(r'\\x(\w{2})')
    content = p.sub(asciirepl, content)
    return json.loads(content)


class Subcenter(subtitles.subtitle.Subtitle):
    def __init__(self):
        super(self.__class__, self).__init__(SUBSCENTER_PAGES.DOMAIN)
        self.configuration_name = "subcenter"

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
                all_episodes.append({   'season_id': jsoned_series_page_dict[season][episode]['season_id'],
                                        'episode_id': jsoned_series_page_dict[season][episode]['episode_id']})
        return all_episodes

    @staticmethod
    def getVersionsList(versions_json):
        """
            This function will get the versions page of the movie/series and
            return a tuple of vesrions summary and a formatted dictionary where
            each key is the version_sum and the values are movie_code,
            version_code and downloads count.
        """

        # A dictionary where the keys are the version_sum, and the values are
        # dicts of movie_code, version_code and downloads.
        all_versions = {}
        ver_sum = ''

        jsoned_movie_page_dict = getJson(versions_json)
        current_language_providers = \
            jsoned_movie_page_dict[SUBSCENTER_PAGES.LANGUAGE]

        total_qualities = []

        # Extract the qualities from each provider.
        for qualities in current_language_providers.values():
            for quality, versions in qualities.iteritems():
                # Insert to the VerSum if not generic quality (ALL), or
                # alreadt in the list.
                if quality != 'ALL' and not quality in total_qualities:
                    total_qualities.append(quality)

                for version in versions.values():
                    # Use the version as version sum.
                    version_sum = version['subtitle_version']
                    downloads = int(version['downloaded'])

                    version_in_dict = all_versions.get(version_sum)
                    # If not in the dict, or the one in the dict has less
                    # downloads, put the new one in the dict.
                    if not version_in_dict or \
                                    version_in_dict['downloads'] <= downloads:
                        all_versions[version_sum] = {
                            "movie_code": version['id'],
                            "version_code": version['key'],
                            'downloads': downloads
                        }

        ver_sum = ' / '.join(total_qualities)

        return (ver_sum, all_versions)

    def _getMovieSubStageForMovie(self, movie_name, movie_code):
        versions_json = self.urlHandler.request(
            SUBSCENTER_PAGES.DOMAIN,
            SUBSCENTER_PAGES.MOVIE_JSON % movie_code)

        (ver_sum, all_versions) = \
            self.getVersionsList(versions_json)

        return (
            movie_name,
            movie_code,
            ver_sum,
            # Add special info.
            {'type': 'movie', 'all_versions': all_versions})


    def _getMovieSubStagesForSeries(self, cls, series_name, movie_code):
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
                cls.PROVIDER_NAME,
                '%s %s' % (series_name, fotmatted_episode),
                '%s/%s/%s' % (movie_code, season_id, episode_id),
                default_versum,
                {'type': 'series'})

    def findSubtitles(self, contentToDownload):
        moviename = contentToDownload.title
        _movie_sub_stages = []

        result_page = self.urlHandler.request(
            SUBSCENTER_PAGES.DOMAIN,
            SUBSCENTER_PAGES.SEARCH % moviename.replace(' ', '+'))

        movies_info = Utils.getregexresults(
            SUBSCENTER_REGEX.SEARCH_RESULTS_PARSER, result_page, True)

        for movie_info in movies_info:
            movie_code = movie_info['Code']
            movie_type = movie_info['Type']
            movie_name = movie_info['MovieName']

            try:
                # Left side is the hebrew name, the right is english.
                movie_name = movie_name.split(' / ')[1]
            except:
                # If failed, keep the original name.
                movie_name = movie_info['MovieName']

            if movie_type == 'movie' == contentToDownload.movieOrSeries:
                _movie_sub_stages.append(self._getMovieSubStageForMovie(movie_name, movie_code))

            elif movie_type == 'series' == contentToDownload.movieOrSeries:
                for stage in self._getMovieSubStagesForSeries(movie_name, movie_code): ###
                    _movie_sub_stages.append(stage)

        return _movie_sub_stages

    def findVersionSubStageList(self, cls, movie_sub_stage):

        # A dictionary where keys are the version_sum and the values are dicts
        # with movie_code and version_code.
        all_versions = {}

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

                    cls.PROVIDER_NAME,
                    version_sum,
                    item['version_code'],
                    item['movie_code'])

        return version_sub_stages

    def download_subtitle(self, version_sub_stage, filename):
        download_page = SUBSCENTER_PAGES.DOWN_PAGE % (
        SUBSCENTER_PAGES.LANGUAGE,
        version_sub_stage.movie_code,
        # Replace spaces with their code
        version_sub_stage.version_sum.replace(' ', '%20'),
        version_sub_stage.version_code)

        f = self.urlHandler.request(self.domain, download_page)
        with open(filename, "wb") as subFile:
            subFile.write(f)
        subFile.close()

    def _is_logged_in(self, url):
        pass

    def login(self):
        pass

if __name__ == "__main__":
    c = content.Content("12 years a slave", "movie")
    sc = Subcenter()
    sc.findSubtitles(c)
    print 4