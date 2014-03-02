#coding=utf8
import urllib
import urllib2
import urlparse
import cookielib
import re
import json

# TODO: fix the url /gui/ thingy

class UTorrentClient(object):
    def __init__(self, base_url='http://localhost.:8080', username='admin', password='admin'):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.opener = self._make_opener('uTorrent', base_url, username, password)
        self.token = self._get_token()
        #TODO refresh token, when necessary

    def _make_opener(self, realm, base_url, username, password):
        """uTorrent API need HTTP Basic Auth and cookie support for token verify."""

        auth_handler = urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password(realm=realm,
                                  uri=base_url,
                                  user=username,
                                  passwd=password)
        opener = urllib2.build_opener(auth_handler)
        urllib2.install_opener(opener)

        cookie_jar = cookielib.CookieJar()
        cookie_handler = urllib2.HTTPCookieProcessor(cookie_jar)

        handlers = [auth_handler, cookie_handler]
        opener = urllib2.build_opener(*handlers)
        return opener

    def _get_token(self):
        url = urlparse.urljoin(self.base_url, 'gui/token.html')
        response = self.opener.open(url)
        token_re = "<div id='token' style='display:none;'>([^<>]+)</div>"
        match = re.search(token_re, response.read())
        return match.group(1)

    def list(self, **kwargs):
        params = [('list', '1')]
        params += kwargs.items()
        return self._action(params)

    def add_url(self, url):
        #can recieve magnet or normal .torrent link
        params = [('action', 'add-url'), ('s', url)]
        return self._action(params)

    def start(self, *hashes):
        params = [('action', 'start'), ]
        for hash in hashes:
            params.append(('hash', hash))
        return self._action(params)

    def stop(self, *hashes):
        params = [('action', 'stop'), ]
        for hash in hashes:
            params.append(('hash', hash))
        return self._action(params)

    def pause(self, *hashes):
        params = [('action', 'pause'), ]
        for hash in hashes:
            params.append(('hash', hash))
        return self._action(params)

    def forcestart(self, *hashes):
        params = [('action', 'forcestart'), ]
        for hash in hashes:
            params.append(('hash', hash))
        return self._action(params)

    def getfiles(self, hash):
        params = [('action', 'getfiles'), ('hash', hash)]
        return self._action(params)

    def getprops(self, hash):
        params = [('action', 'getprops'), ('hash', hash)]
        return self._action(params)

    def setprops(self, hash, **kvpairs):
        params = [('action', 'setprops'), ('hash', hash)]
        for k, v in kvpairs.iteritems():
            params.append(("s", k))
            params.append(("v", v))

        return self._action(params)

    def setprio(self, hash, priority, *files):
        params = [('action', 'setprio'), ('hash', hash), ('p', str(priority))]
        for file_index in files:
            params.append(('f', str(file_index)))

        return self._action(params)

    def _action(self, params, body=None, content_type=None):
        url = self.base_url + '/gui/' + '?token=' + self.token + '&' + urllib.urlencode(params)
        request = urllib2.Request(url)

        if body:
            request.add_data(body)
            request.add_header('Content-length', len(body))
        if content_type:
            request.add_header('Content-type', content_type)

        try:
            response = self.opener.open(request)
            return response.code, json.loads(response.read())
        except urllib2.HTTPError, e:
            raise
