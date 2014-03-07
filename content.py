

class Content(object):
    def __init__(self, name, movieOrSeries, season=0, episodeNumber=0, wholeSeasonFlag=False, wholeSeriesFlag=False):
        self.title = name
        self.movieOrSeries = movieOrSeries
        self.episodeNumber = episodeNumber
        self.season = season
        self.wholeSeasonFlag = wholeSeasonFlag
        self.wholeSeriesFlag = wholeSeriesFlag
