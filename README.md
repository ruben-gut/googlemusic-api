googlemusic-api
===============

Python client API for accessing Google Music API. Work in progress.

##Requierements

Python 2.6 or above should be enough. Though, it was only fully tested on 2.7.2
under OS X 10.7 and OS X 10.8.

No third party libraries or modules are necessary.

##Usage

The end-user entry point is the Client class.

    from googlemusic.client import Client
    
    client = Client()
    client.login('email@gmail.com', 'p4ssw0rd')

You can then perform several different operations.

Get all the user's playlists (including their songs information)

    playlists = client.get_all_playlists()

    # iterate the list of playlists
    for playlist in playlists:
        print playlist

    # iterate the list of songs of a playlist
    playlist = playlists[0]
    for song in playlist.songs:
        print song

Perform a search.

    results = client.search('Some Search Text')
    for song in results['Songs']:
        print song

Download a song in MP3 format.

    song = playlist.songs[0]
    client.download_song(song, '/Users/tirino/mp3s/')


For a complete list of available commands take a look at the methods of the
Client class.

TODO
====
* Improve documentation
* Add support to upload music

Credits
=======
Author:
* Tirino - http://github.com/tirino

Feel free to port this library to other languages or to take any ideas or
hints from this code.
