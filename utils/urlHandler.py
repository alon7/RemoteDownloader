import os
import urllib
import urllib2
import urlparse
import zlib
import cookielib


# TODO: fix request method

class URLHandler():
    def __init__(self):
        self.cookie_filename = os.path.join("cookiejar.txt")  # change to default download path in configuration file
        self.cookie_jar = cookielib.LWPCookieJar(self.cookie_filename)
        if os.access(self.cookie_filename, os.F_OK):
            self.cookie_jar.load()

        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie_jar))
        self.opener.addheaders = [('Accept-Encoding', 'gzip'),
                                  ('Accept-Language', 'en-us,en;q=0.5'),
                                  ('Pragma', 'no-cache'),
                                  ('Cache-Control', 'no-cache'),
                                  ('User-Agent',
                                   'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:16.0) Gecko/20100101 Firefox/16.0')]

    def request(self, domain, url, data=None, decode_zlib=True, ajax=False, referer=None, cookie=None):

        uri = urlparse.urljoin(domain, url)

        if data is not None:
            data = urllib.urlencode(data)
        if ajax:
            self.opener.addheaders += [('X-Requested-With', 'XMLHttpRequest')]
        if referer is not None:
            self.opener.addheaders += [('Referer', referer)]
        if cookie is not None:
            self.opener.addheaders += [('Cookie', cookie)]

        content = None
        try:
            response = self.opener.open(uri, data)
            if response.code != 200:
                content = None
            else:
                content = response.read()

            if decode_zlib and response.headers.get('content-encoding', '') == 'gzip':
                try:
                    content = zlib.decompress(content, 16 + zlib.MAX_WBITS)
                except zlib.error:
                    pass

            response.close()
        except Exception as e:
            print "Failed to get url: %s\n%s" % (url, e)
        return content

    def save_cookie(self):
        self.cookie_jar.save()