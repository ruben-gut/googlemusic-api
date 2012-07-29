"""
Google Music API
"""
__author__ = "Tirino"
#
# If you've got decoding issues with non-ascii characters in the console:
# 
# import sys
# sys.setdefaultencoding( "utf8" )
#

def test_api(username, password):
    """Very simple test"""
    from googlemusic.client import Client
    client = Client()
    client.set_debug(True)
    client.login(username, password)
    playlists = client.get_all_playlists()
    for playlist in playlists:
        print playlist
    return client

