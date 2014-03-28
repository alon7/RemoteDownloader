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
