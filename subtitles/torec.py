import subtitles.subtitle
import re


class Torec(subtitles.Subtitle):
    def __init__(self):
        pass

    def _is_logged_in(self, url):
        content = self.urlHandler.request(url)
        if content is not None and re.search(r'friends\.php', content):  #  check if logged in
            return content
        elif self.login():
            return self.urlHandler.request(url)
        else:
            return None

    def login(self):
        email = self.configuration.get("subtitlescoil", "email")
        password = self.configuration.get("subtitlescoil","password")
        query = {'email': email, 'password': password, 'Login': 'התחבר'}
        content = self.urlHandler.request(self.BASE_URL + "/login.php", query)
        if re.search(r'<form action="/login\.php"', content):
            return None
        else:
            self.urlHandler.save_cookie()
            return True
