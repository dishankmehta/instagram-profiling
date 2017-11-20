import tempfile
import requests
import os
import utils
import six


class Login:
    username = None
    password = None

    def __init__(self, username, password):
        self.username = username
        self.password = password

    URL_HOME = "https://www.instagram.com/"
    URL_LOGIN = "https://www.instagram.com/accounts/login/ajax/"
    URL_LOGOUT = "https://www.instagram.com/accounts/logout/"

    session = requests.Session()

    COOKIE_FILE = os.path.join(tempfile.gettempdir(), "InstaCrawler", "cookies.txt")
    session.cookies = six.moves.http_cookiejar.LWPCookieJar(COOKIE_FILE)

    def login_user(self):
        login_post = {'username': self.username,
                      'password': self.password}

        self.session.headers.update({
            'Origin': self.URL_HOME,
            'Referer': self.URL_HOME,
            'X-Instragram-AJAX': '1',
            'X-Requested-With': 'XMLHttpRequest', })

        get_token = self.session.get(self.URL_HOME)
        if get_token:
            self.session.headers.update({'X-CSRFToken': get_token.cookies['csrftoken']})

        login = self.session.post(self.URL_LOGIN, data=login_post, allow_redirects=True)
        if not login.status_code == 200:
            print('Login Error...!!')
            print("Status code: %d" % login.status_code)
        else:
            print("successfully logged in as {}".format(login_post['username']))
            self.session.headers.update({'X-CSRFToken': login.cookies['csrftoken']})

        res = self.session.get(self.URL_HOME)
        if res.text.find(login_post['username']) == -1:
            print('No username!!')
        utils.save_cookies(self.session)

    def logout_user(self):
        logout_post = {'csrfmiddlewaretoken': self.session.cookies._cookies.get(
            "www.instagram.com", {"/": {}})["/"].get("sessionid") is not None
        }

        self.session.post(self.URL_LOGOUT, data=logout_post)
        if os.path.isfile(self.COOKIE_FILE):
            os.remove(self.COOKIE_FILE)

    def is_logged_in(self):
        return self.session.cookies._cookies.get(
            "www.instagram.com", {"/": {}})["/"].get("sessionid") is not None
