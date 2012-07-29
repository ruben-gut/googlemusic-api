"""
Google Music Protocol

These classes implement the logic and actual requests made to interact with
Google Music.

If you want to port this project, these classes contain the most useful
information.
"""
__author__ = "Tirino"

import urllib
import random

from googlemusic.request import MusicManagerRequest
from googlemusic.request import FORM_CONTENT_TYPE
from googlemusic.utils import get_from_text

class AuthenticationException(Exception):
    """Exception for authentication errors"""
    pass

class RequestException(Exception):
    """Exception for API request errors"""
    pass

class MusicManagerClient(object):
    """Class to emulate MusicManager Client"""
    ISSUE_AUTH_URL = 'https://www.google.com/accounts/IssueAuthToken'
    ISSUE_AUTH_SERVICE_NAME = 'gaia'
    TOKEN_AUTH_URL = 'https://www.google.com/accounts/TokenAuth'

    def __init__(self, cookies):
        self.cookies = cookies
        self.base_request = MusicManagerRequest(self.cookies)

    def get_issue_auth(self, auth_data, headers):
        """Return an issue auth token"""
        body = {
          'SID': auth_data['SID'], 'LSID': auth_data['LSID'],
          'service': self.ISSUE_AUTH_SERVICE_NAME
        }
        issue_response = self.base_request.request(self.ISSUE_AUTH_URL, 
                                                            body, headers)
        return issue_response.rstrip()

    def authenticate(self, auth_data, service, redirect, source=None):
        """Authenticate against the provided service"""
        headers = {'Content-Type': FORM_CONTENT_TYPE}
        issue_auth = self.get_issue_auth(auth_data, headers)
        params_data = {
          'auth': issue_auth, 'service': service, 'continue': redirect
        }
        if source:
            params_data['source'] = source

        params = urllib.urlencode(params_data)
        url = '%s?%s' % (self.TOKEN_AUTH_URL, params)
        # Get session cookies
        return self.base_request.request(url, None, headers)


class Protocol(object):
    """Google Music Protocol API"""
    SERVICE_NAME = 'sj'
    SERVICE_ENDPOINT = 'https://play.google.com/music/services'
    
    LOGIN_ENDPOINT = 'https://www.google.com/accounts/ClientLogin'
    PLAY_ENDPOINT = 'https://play.google.com/music/play'
    
    GOOGLE_PLAY_URL = 'https://play.google.com/music/listen?u=0&hl=en'
    
    def __init__(self, web_request):
        self.debug = False
        self.session_id = '%.20d' % (1E20 * random.random())
        self.web = web_request
        self.cookies = self.web.get_cookies()
        self.auth_data = {}
        self.playlists = []
    
    def login(self, username, password):
        """Authenticate against Google Music servers"""
        body = {
          'Email': username, 'Passwd': password,
          'service': self.SERVICE_NAME, 'accountType': 'GOOGLE'
        }
        headers = {
          'Accept': '*/*', 'Content-Type': 'application/x-www-form-urlencoded'
        }
        auth_data = self.web.request(self.LOGIN_ENDPOINT, body, headers)
        if 'Auth=' in auth_data:
            self.auth_data['SID'] = get_from_text(r'^SID=(.*)', auth_data)
            self.auth_data['LSID'] = get_from_text(r'LSID=(.*)', auth_data)
            self.auth_data['Auth'] = get_from_text(r'Auth=(.*)', auth_data)
        else:
            raise AuthenticationException(
                                    'Unable to authenticate: %s' % auth_data)
        
        # now get a XT cookie
        mm_client = MusicManagerClient(self.cookies)
        mm_client.authenticate(self.auth_data, self.SERVICE_NAME, 
                                            self.GOOGLE_PLAY_URL, 'jumper')
        self.cookies = mm_client.cookies
        return True
    
    def get_xt_for_url(self):
        """Return the XT code, url encoded"""
        return urllib.quote(self.cookies.get_cookie('xt'))
    
    def api_request(self, method, payload=None):
        """Make XHR requests and parse the result as JSON"""
        payload = payload or {}
        payload['sessionId'] = self.session_id
        body = {'json': payload}
        headers = {'Content-Type': FORM_CONTENT_TYPE}
        url = url = '%s/%s?u=0&xt=%s' % (self.SERVICE_ENDPOINT, method, 
                                                self.get_xt_for_url())
        return self.web.xhr_json(url, body, headers)
    
    # Playlists #
    def get_all_playlists(self):
        """Return all the playlists and their songs"""
        result = self.api_request('loadplaylist', {})
        if 'playlists' in result:
            return result['playlists']
        else:
            raise RequestException("Couldn't get playlists: %s", str(result))
    
    def load_playlist(self, playlist_id):
        """Load a specific playlist's songs"""
        body = {'id': playlist_id, 'requestCause': 3, 'requestType': 1}
        result = self.api_request('loadplaylist', body)
        if 'playlistId' in result:
            return result['playlist']
        else:
            raise RequestException("Couldn't load playlist: %s", str(result))
    
    def add_playlist(self, title):
        """Create a playlist"""
        result = self.api_request('addplaylist', {'title': title})
        if 'success' in result and result['success']:
            return result
        else:
            raise RequestException('Could not add playlist:' % title)
    
    def add_playlist_with_songs(self, title, song_ids=None):
        """Add a Playlist and assign the passed songs to it"""
        # https://play.google.com/music/services/addplaylist?u=0&xt=Cj...U==
        # POST
        # json={"title":"TestPL","songIds":[],"sessionId":"60...0"}
        # RES: {"id":"87c6bc8c...d9672d97","title":"TestPL","success":true}
        song_ids = song_ids or []
        body = {'title': title, 'songIds': song_ids}
        result = self.api_request('addplaylist', body)
        if 'success' in result and result['success']:
            return result
        else:
            raise RequestException('Could not add playlist:' % title)
    
    def modify_playlist(self, playlist_id, title):
        """Modify (currently just 'rename') a Playlist"""
        body = {'playlistId': playlist_id, 'playlistName': title}
        result = self.api_request('modifyplaylist', body)
        # if we received an empty dict, it went ok
        if (isinstance(result, dict) and not result):
            return True
        else:
            raise RequestException(
                            'Could not modify playlist: %s' % str(result))
    
    def delete_playlist(self, playlist_id):
        """Delete a Playlist"""
        body = {'id': playlist_id, 'requestCause': 1, 'requestType' :1}
        result = self.api_request('deleteplaylist', body)
        if ('deleteId' in result and result['deleteId'] == playlist_id):
            return True
        else:
            raise RequestException(
                            'Could not delete playlist: %s' % str(result))
    
    # General #
    
    def search(self, query):
        """Search the user's library"""
        result = self.api_request('search', {'q': query})
        if 'results' in result:
            return result['results']
        else:
            raise RequestException('Could not perform search!')
    
    def get_stream_url(self, song_id):
        """Get the URL to stream or download a song"""
        url = '%s?u=0&songid=%s&pt=e' % (self.PLAY_ENDPOINT, song_id)
        result = self.web.xhr_json(url)
        if 'url' in result:
            return result
        else:
            raise RequestException('Could not get the URL: %s' % str(result))
    
    def get_settings(self):
        """Get the user settings"""
        # URL: /services/loadsettings?u=0&xt=Cj...U==
        # Request Method:POST
        # json=%7B%22sessionId%22%3A%....00%22%7D
        return self.api_request('loadsettings')
    
    def modify_labs(self, srv, value):
        """Modify a Google Music Labs setting"""
        # https://play.google.com/music/services/modifylab?u=0&xt=Cj...U==
        # Request Method:POST
        # json={"labs":{"sr":false},"sessionId":"379....000"}
        return self.api_request('modifylabs', {'labs': {srv: value}})

