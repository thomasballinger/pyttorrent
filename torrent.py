#!/usr/bin/env python
import argparse
import bencode
import math
import os
import sys
import urllib2

from lib.handshake import HandShake
from lib.torrentfile import TorrentFile
from lib.tracker import Tracker


def main():
    # get filename from the command line argument
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-f', '--file',
                        required=True,
                        dest = 'file',
                        type = argparse.FileType('r'))

    args = parser.parse_args()
    filename = os.path.abspath(args.file.name)

    # get torrent file data
    torrentfile = TorrentFile(filename)
    url = torrentfile.get_tracker_request_url()

    downloading_file = os.path.abspath('../related_assets/downloads/%s' % torrentfile.filename)
    file = open(downloading_file, 'wb')

    # client_handshake
    client_handshake = HandShake()
    client_handshake.set_default_values(torrentfile.info_hash)
    
    # tracker
    tracker = Tracker(url, str(client_handshake))
    tracker.send_request()
    
    # add peers to the tracker peers collection
    peers_list = tracker.get_peers_list()
    tracker.add_peers(peers_list)
    
    """
    TODO -- remove the lines below
    """ 
    peer = tracker.get_peer_by_ip_port('96.126.104.219', 65373)
    peer.connection.open()
    peer.connection.send_data(str(client_handshake))

    # create peer handshake instance
    peer_handshake_string = peer.connection.recv_data()
    peer_handshake = HandShake()
    peer_handshake.set_handshake_data_from_string(peer_handshake_string)

    data = peer.connection.recv_data()
    peer.append_to_buffer(data)
    peer.consume_messages()

    msg = peer.get_interested_message()
    peer.connection.send_data(msg)
    data = peer.connection.recv_data()

    peer.append_to_buffer(data)
    peer.consume_messages()

    requested_length = int(math.pow(2,14))

    for i in range(0, 78):
        msg = peer.get_request_piece_message(i, 0, requested_length)
        peer.connection.send_data(msg)

        data = peer.connection.recv_data()
        data_length = peer.get_4_byte_to_decimal(data[0:4])

        # keep receiving data until you have the entire block
        while len(data) < data_length + 4:
            data += peer.connection.recv_data()
        peer.append_to_buffer(data)
        peer.consume_messages()
    
    # get last piece (which is smaller than the rest)
    msg = peer.get_request_piece_message(78, 0, 35)
    peer.connection.send_data(msg)
    data = peer.connection.recv_data()
    data_length = peer.get_4_byte_to_decimal(data[0:4])
    
    # keep receiving data until you have the entire block
    while len(data) < data_length + 4:        
        data += peer.connection.recv_data()
    peer.append_to_buffer(data)
    peer.consume_messages()
    
    
if __name__ == "__main__":
    main()
