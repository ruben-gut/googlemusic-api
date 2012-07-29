"""
Google Music client

A simple Client to interact with Google Music
"""
__author__ = "Tirino"

from googlemusic.model import Album, Song, Playlist
from googlemusic.protocol import Protocol
from googlemusic.request import CookieManager, WebRequest

class Client(object):
    """Client API class"""
    def __init__(self):
        self.debug = False
        self.cookies =  CookieManager()
        self.web = WebRequest(self.cookies)
        self.protocol = Protocol(self.web)
        self.playlists = []
    
    def set_debug(self, debug):
        """Enable debug mode"""
        self.debug = debug
        self.web.debug = self.debug
        self.protocol.debug = self.debug
    
    def login(self, username, password):
        """Log the user in"""
        return self.protocol.login(username, password)
    
    # Playlists #
    def get_all_playlists(self):
        """Return a list of Playlist objects with embedded Song objects"""
        result = []
        playlists_data = self.protocol.get_all_playlists()
        for playlist_data in playlists_data:
            result.append(Playlist(playlist_data))
        return result
    
    def load_playlist(self, playlist):
        """Given a Playlist object populate it with its Song objects"""
        songs_data = self.protocol.load_playlist(playlist.id)
        for song_data in songs_data:
            playlist.songs.append(Song(song_data))
        return playlist
    
    def add_playlist(self, title):
        """Create a playlist"""
        return Playlist(self.protocol.add_playlist(title))

    def add_playlist_with_songs(self, title, songs=None):
        """Create a Playlist and add the given songs to it"""
        if songs:
            song_ids = [song.id for song in songs]
        else:
            song_ids = []
        return Playlist(self.protocol.add_playlist_with_songs(title, song_ids))

    def modify_playlist(self, playlist, title):
        """Rename a Playlist"""
        return self.protocol.modify_playlist(playlist.id, title)

    def delete_playlist(self, playlist):
        """Delete a Playlist object from the user's library"""
        return self.protocol.delete_playlist(playlist.id)

    def get_stream_url(self, song):
        """Obtain the stream/download URL for a specific song"""
        return self.protocol.get_stream_url(song.id)

    def get_settings(self):
        """Return a dict with the user Google Music's Settings"""
        return self.protocol.get_settings()

    def search(self, query):
        """Return a dict with Albums and Songs that match the given query"""
        # TODO: add Artists as well
        result = {'Albums': [], 'Songs': []}
        result_data = self.protocol.search(query)
        for album_data in result_data['albums']:
            result['Albums'].append(Album(album_data))
        for song_data in result_data['songs']:
            result['Songs'].append(Song(song_data))
        return result

    def download_song(self, song, to_folder='.'):
        """Download the mp3 file of the given Song object"""
        url_data = self.protocol.get_stream_url(song.id)
        filename = '%s/%s - %s.mp3' % (to_folder, song.artist, song.title)
        return self.web.download_file(url_data['url'], filename)

