

class Content(object):
    def __init__(self, name, movieOrSeries, version=None, season=0, episodeNumber=0, wholeSeasonFlag=False, wholeSeriesFlag=False):
        self.title = name
        self.movieOrSeries = movieOrSeries
        self.versions = [version]
        self.episodeNumber = episodeNumber
        self.season = season
        self.wholeSeasonFlag = wholeSeasonFlag
        self.wholeSeriesFlag = wholeSeriesFlag
        if movieOrSeries == 'series':
            self.modifiedName = self.getModifiedName()
        else:
            self.modifiedName = self.title

    def getModifiedName(self):
        formatedEpisode = 'S%sE%s' % (self.season.rjust(2, '0'), self.episodeNumber.rjust(2, '0'))
        return '%s %s' % (self.title, formatedEpisode)