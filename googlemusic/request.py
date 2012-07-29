"""
Google Music Request handlers

These classes mimic requests made by a Web Browser and Google Music Manager
"""
__author__ = "Tirino"

import cookielib
import urllib
import urllib2
try:
    import simplejson as json
except ImportError:
    import json

FORM_CONTENT_TYPE = 'application/x-www-form-urlencoded;charset=UTF-8'

class CookieManager(cookielib.CookieJar):
    """Class to store and retrieve Cookies"""
    def __init__(self):
        cookielib.CookieJar.__init__(self)

    def get_cookie(self, name):
        """Return the first cookie with the given name"""
        for cookie in self:
            if cookie.name == name:
                return cookie.value
        return None


class MusicManagerRequest(object):
    """Class to emulate MusicManager requests"""
    USER_AGENT = 'Music Manager (1, 0, 24, 7712 - Windows)'

    def __init__(self, cookies):
        self.cookies = cookies

    def request(self, url, body=None, headers=None):
        """Wrapper to make all requests"""
        headers = headers or {}
        if body:
            body = urllib.urlencode(body).encode('utf8')
        
        if 'User-Agent' not in headers:
            headers['User-Agent'] = self.USER_AGENT

        request = urllib2.Request(url, body, headers)
        handler = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(self.cookies)
        )
        response = handler.open(request)
        result = response.read()
        response.close()
        return unicode(result, encoding='utf8')

    def get_cookies(self):
        """Return the Cookie Manager object"""
        return self.cookies
    
class WebRequest(object):
    """
    Class to mimic Web requests.
    Depends on MusicManager and CookieManager
    """
    USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) ' \
            'AppleWebKit 536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 ' \
            'Safari/536.11'
    
    DEFAULT_ORIGIN = 'https://play.google.com'
    DEFAULT_REFERER = 'https://play.google.com/music/listen'
    
    DOWNLOAD_CHUNK = 512 * 1024
    
    def __init__(self, cookies):
        self.debug = False
        self.cookies = cookies

    def request(self, url, body=None, headers=None, xhr=False):
        """Wrapper to make all web requests."""
        headers = headers or {}
        if body:
            body = urllib.urlencode(body).encode('utf8')

        # Apply default headers if necessary
        headers['DNT'] = 1 # Do Not Track
        if not 'User-Agent' in headers:
            headers['User-Agent'] = self.USER_AGENT
        if xhr:
            if not 'Origin' in headers:
                headers['Origin'] = self.DEFAULT_ORIGIN
            if not 'Referer' in headers:
                headers['Referer'] = self.DEFAULT_REFERER
            headers['X-Requested-With'] = 'XMLHttpRequest'

        if self.debug:
            print ">>> URL: %s" % url
            print ">>> Body: %s" % body
            print ">>> Headers: %s" % str(headers) 
        
        request = urllib2.Request(url, body, headers)
        handler = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(self.cookies)
        )

        response = handler.open(request)
        result = response.read()
        response.close()
        return unicode(result, encoding='utf8')

    def xhr_json(self, url, body=None, headers=None):
        """Make an XHR request and return its result as JSON"""
        return json.loads(self.request(url, body, headers, xhr=True))
    
    def download_file(self, url, filename):
        """Download a file to the specified location"""
        headers = {
          'Referer': self.DEFAULT_REFERER,
          'User-Agent': self.USER_AGENT
        }
        request = urllib2.Request(url, None, headers)
        handler = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(self.cookies)
        )
        source = handler.open(request)
        
        downloaded = 0
        total_size = 0
        content_length = source.info().getheader('Content-Length')
        if content_length:
            total_size = int(content_length.strip())

        with open(filename, 'wb') as dest:
            while True:
                chunk = source.read(self.DOWNLOAD_CHUNK)
                if not chunk:
                    break
                downloaded += len(chunk)
                dest.write(chunk)
                if total_size and self.debug:
                    progress = int((float(downloaded) / total_size) * 100)
                    print '%s%%' % progress
        return True
    
    def get_cookies(self):
        """Return the Cookie Manager object"""
        return self.cookies
 
