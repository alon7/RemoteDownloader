import re

# TODO: unzip subtitles zip files


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