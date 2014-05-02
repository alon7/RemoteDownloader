import re
import time
import cProfile

# TODO: unzip subtitles zip files


def do_cprofile(func):
    def profiled_func(*args, **kwargs):
        #profile = cProfile.Profile()
        #try:
            #profile.enable()
        result = func(*args, **kwargs)
            #profile.disable()
        return result
        #finally:
            #profile.print_stats(sort="tottime")
    return profiled_func


def getregexresults(pattern, content, with_groups=False):
    c_pattern = re.compile(pattern)
    results = []
    if with_groups:
        results = map(lambda i: i.groupdict(), re.finditer(c_pattern, content))
    else:
        results = re.findall(c_pattern, content)
    return list(results)


def bytes_converter(num, size_or_speed):
    if size_or_speed == 'speed':
        ret_string = "\s"
    elif size_or_speed == 'size':
        ret_string = ""

    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s%s" % (num, x, ret_string)
        num /= 1024.0


def versionMatching(torrentName, subtitleName):
    match = False
    if torrentName == subtitleName:
        match = True
    elif torrentName.replace(' ', '.') == subtitleName.replace(' ', '.'):
        match = True
    elif torrentName[:torrentName.find('[')] == subtitleName:
        match = True
    elif torrentName[:torrentName.find('[')].replace(' ', '.') == subtitleName.replace(' ', '.'):
        match = True
    elif re.sub('[-.]', ' ', torrentName[:torrentName.find('[')]) == re.sub('[-.]', ' ', subtitleName):
        match = True
    elif re.sub('[-.]', ' ', torrentName) == re.sub('[-.]', ' ', subtitleName):
        match = True
    return match

def timefunc(f):
    def f_timer(*args, **kwargs):
        #start = time.time()
        result = f(*args, **kwargs)
        #end = time.time()
        #print f.__name__, 'took', end - start, 'time', f.func_globals.get("__name__")
        return result
    return f_timer