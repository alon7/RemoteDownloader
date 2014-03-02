# -*- coding: utf-8 -*-

import subtitles.subtitle
import re
import urllib


class SubtitleCoIl(subtitles.subtitle.Subtitle):
    def __init__(self):
        super(self.__class__, self).__init__("http://www.subtitle.co.il/")
        self.configuration_name = "subtitlescoil"

    def get_subtitle_list(self, item):
        if item["tvshow"]:
            search_results = self._search_tvshow(item)
            results = self._build_tvshow_subtitle_list(search_results, item)
        else:
            search_results = self._search_movie(item)
            results = self._build_movie_subtitle_list(search_results, item)

        return results

    # return list of tv-series from the site`s search
    def _search_tvshow(self, item):
        search_string = re.split(r'\s\(\w+\)$', item["tvshow"])[0]

        results = None

        if not results:
            query = {"q": search_string.lower(), "cs": "series"}

            search_result = self.urlHandler.request(self.base_url + "/browse.php?" + urllib.urlencode(query))
            if search_result is None:
                return results  # return empty set

            urls = re.findall(
                u'<a href="viewseries\.php\?id=(\d+)[^"]+" itemprop="url">[^<]+</a></div><div style="direction:ltr;" class="smtext">([^<]+)</div>',
                search_result)

            results = self._filter_urls(urls, search_string, item)
        else:
            results = eval(results)

        return results

    # return list of movie from the site`s search
    def _search_movie(self, item):
        results = []
        search_string = item["title"]
        query = {"q": search_string.lower(), "cs": "movies"}
        if item["year"]:
            query["fy"] = int(item["year"]) - 1
            query["uy"] = int(item["year"]) + 1

        search_result = self.urlHandler.request(self.base_url + "/browse.php?" + urllib.urlencode(query))
        if search_result is None:
            return results  # return empty set

        urls = re.findall(
            u'<a href="view\.php\?id=(\d+)[^"]+" itemprop="url">[^<]+</a></div><div style="direction:ltr;" class="smtext">([^<]+)</div><span class="smtext">(\d{4})</span>',
            search_result)

        results = self._filter_urls(urls, search_string, item)
        return results

    def _filter_urls(self, urls, search_string, item):
        filtered = []
        search_string = search_string.lower()

        if not item["tvshow"]:
            for (id, eng_name, year) in urls:
                if search_string.startswith(eng_name.lower()) and \
                        (item["year"] == '' or
                                 year == '' or
                                     (int(year) - 1) <= int(item["year"]) <= (int(year) + 1) or
                                     (int(item["year"]) - 1) <= int(year) <= (int(item["year"]) + 1)):
                    filtered.append({"name": eng_name, "id": id, "year": year})
        else:
            for (id, eng_name) in urls:
                if search_string.startswith(eng_name.lower()):
                    filtered.append({"name": eng_name, "id": id})

        return filtered

    def _build_movie_subtitle_list(self, search_results, item):
        ret = []
        total_downloads = 0
        for result in search_results:
            url = self.base_url + "/view.php?" + urllib.urlencode({"id": result["id"], "m": "subtitles"})
            subtitle_page = self._is_logged_in(url)
            x, i = self._retrive_subtitles(subtitle_page, item)
            total_downloads += i
            ret += x

        # Fix the rating
        if total_downloads:
            for it in ret:
                it["rating"] = str(int(round(it["rating"] / float(total_downloads), 1) * 5))

        return sorted(ret, key=lambda x: (x['lang_index'], x['sync'], x['rating']), reverse=True)

    def download_subtitle(self, id, zip_filename):
        query = {"id": id}
        url = self.BASE_URL + "/downloadsubtitle.php?" + urllib.urlencode(query)
        f = self.urlHandler.request(url)

        with open(zip_filename, "wb") as subFile:
            subFile.write(f)
        subFile.close()

    def _is_logged_in(self, url):
        content = self.urlHandler.request(url)
        if content is not None and re.search(r'friends\.php', content):
            return content
        elif self.login():
            return self.urlHandler.request(url)
        else:
            return None

    def login(self):
        email = self.configuration.get(self.configuration_name, "email")
        password = self.configuration.get(self.configuration_name,"password")
        query = {'email': email, 'password': password, 'Login': 'התחבר'}
        content = self.urlHandler.request(self.base_url + "/login.php", query)
        if re.search(r'<form action="/login\.php"', content):
            return None
        else:
            self.urlHandler.save_cookie()
            return True

def main():
    s = SubtitleCoIl()
    flag = s._is_logged_in(s.base_url)
    flag2 = s._is_logged_in(s.base_url)
    print flag, flag2

if __name__ == "__main__":
    main()