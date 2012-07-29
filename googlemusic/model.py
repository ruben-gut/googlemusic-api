"""
Google Music models
"""
__author__ = "Tirino"

class Playlist(object):
    """A Google Music Playlist"""
    def __init__(self, data=None):
        if data:
            if 'playlistId' in data:
                self.id = str(data['playlistId'])
            else:
                self.id = str(data['id'])
            self.title = data['title']
            self.songs = []
            if 'playlist' in data:
                for song in data['playlist']:
                    self.songs.append(Song(song))
        else:
            self.id = None
            self.title = None
            self.songs = []

    def __str__(self):
        return ' - '.join([self.id, self.title])

class Album(object):
    """A Google Music Album"""
    def __init__(self, data=None):
        if data:
            self.name = data['albumName']
            self.artist = data['artistName']
            self.album_artist = data['albumArtist']
            if 'imageUrl' in data:
                self.artwork_url = data['imageUrl']
            else:
                self.artwork_url = None
        else:
            self.name = None
            self.artist = None
            self.album_artist = None
            self.artwork_url = None
        
    def get_artwork_url(self):
        """Return the album cover's URL"""
        if self.artwork_url:
            return 'http:%s' % self.artwork_url
        else:
            return None


class Song(object):
    """A Google Music Song"""
    def __init__(self, data=None):
        if data:
            self.id = str(data['id'])
            self.name = data['name']
            self.title = data['title']
            self.artist = data['artist']
            self.album = data['album']
            self.track = data['track']
            if 'albumArtUrl' in data:
                self.artwork_url = data['albumArtUrl']
            else:
                self.artwork_url = None
        else:
            self.id = None
            self.name = None
            self.title = None
            self.artist = None
            self.album = None
            self.track = None
            self.artwork_url = None

    def get_artwork_url(self):
        """Return the album cover's URL"""
        if self.artwork_url:
            return 'http:%s' % self.artwork_url
        else:
            return None

    def __str__(self):
        return ' - '.join([self.id, self.artist, self.title])
