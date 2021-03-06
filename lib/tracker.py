import bencode
import struct
import urllib2

from peer import Peer, PeerCollection

BYTES_IN_IP = 6


class Tracker(object):
    def __init__(self, requesturl, handshake):
        self.requesturl = requesturl
        self.decoded_response = None
        self.peers = PeerCollection()
        self.handshake = handshake
    
    
    def send_request(self):
        response = urllib2.urlopen(self.requesturl).read()
        self.decoded_response = bencode.bdecode(response)
        
        
    def has_binary_peers(self):
        peers = self.decoded_response['peers']
        return not isinstance(peers, list)    
    
    
    def add_peers(self, peers_list):
        for peer_obj in peers_list:
            peer = Peer(peer_obj['ip'], peer_obj['port'], self.handshake)
            self.peers.add(peer)
    
    
    def get_peers_list(self):
        if not self.has_binary_peers():
            return self.decoded_response['peers']
        
        return self.get_binary_peers_list()
    
    
    def get_peer_by_ip_port(self, ip, port):
        return self.peers.get_peer_by_ip_port(ip, port)
    
    
    def get_binary_peers_list(self):
        peers_list = []
        peers = self.decoded_response['peers']
        
        index_start = 0
        index_curr = 0
        index_end = len(peers) - 1
        
        while(index_start < index_end):
            # get block
            binary_peer_block = peers[index_start : index_start + BYTES_IN_IP]
            
            # add peer info dictionary to list
            peer_dict = self.get_binary_peer_dict(binary_peer_block)
            peers_list.append(peer_dict)
            
            # increment index start by the next block size
            index_start += BYTES_IN_IP
            
        return peers_list
    
    
    def get_peer_ipaddress(self, bytes):
        ip_addr = []
        ip_addr.append(str(struct.unpack('B', bytes[0])[0]))
        ip_addr.append(str(struct.unpack('B', bytes[1])[0]))
        ip_addr.append(str(struct.unpack('B', bytes[2])[0]))
        ip_addr.append(str(struct.unpack('B', bytes[3])[0]))
        return '.'.join(ip_addr)
    
    
    def get_peer_port(self, bytes):
        return struct.unpack('B', bytes[0])[0] * 256 + struct.unpack('B', bytes[1])[0]
    
    
    def get_binary_peer_dict(self, block):
        return {
            'ip': self.get_peer_ipaddress(block[0:4]),
            'port': self.get_peer_port(block[4:])
        }
