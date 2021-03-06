import math
import struct

from bitstring import BitArray
from lib.connection import Connection

MSG_LENGTH_SIZE = 4

ID_CHOKE = 0
ID_UNCHOKE = 1
ID_INTERESTED = 2 
ID_NOT_INTERESTED =3 
ID_HAVE = 4
ID_BITFIELD = 5
ID_REQUEST = 6
ID_PIECE = 7
ID_CANCEL = 8
ID_PORT = 9


class Peer(object):
    def __getattr__(self, att):
        def temp():
            self.connection.send_data(getattr(self, 'get_'+att))


    def __init__(self, ip, port, handshake, id=''):
        self.ip = ip
        self.port = port
        self.id = id

        self._buffer = ''
        self.bitfield = None
        self.connection = Connection(self.ip, self.port)

    def append_to_buffer(self, data):
        self._buffer += data


    def consume_messages(self):
        while len(self._buffer) > MSG_LENGTH_SIZE:
            self.consume_message()


    def consume_message(self):
        if len(self._buffer) < MSG_LENGTH_SIZE:
            return

        msg_len = self.get_4_byte_to_decimal(self._buffer[0:MSG_LENGTH_SIZE])

        if len(self._buffer[1:]) < msg_len:
            return

        msg_id, msg_payload = self.get_msg_id_payload(
                self._buffer[MSG_LENGTH_SIZE : MSG_LENGTH_SIZE+msg_len])

        handler = self.get_msg_handler(msg_id)
        if handler:
            handler(msg_len, msg_payload)

        self._buffer = self._buffer[MSG_LENGTH_SIZE+msg_len:]


    def get_4_byte_to_decimal(self, msg):
        msg_len = 0

        msg_len += struct.unpack('B', msg[0])[0] * int(math.pow(256, 3))
        msg_len += struct.unpack('B', msg[1])[0] * int(math.pow(256, 2))
        msg_len += struct.unpack('B', msg[2])[0] * int(math.pow(256, 1))
        msg_len += struct.unpack('B', msg[3])[0]

        return msg_len
        
    def get_msg_id_payload(self, msg):
        msg_id = struct.unpack('B', msg[0])[0]
        payload = msg[1:]
        return msg_id, payload
        
    def get_msg_handler(self, msg_id):
        if ID_CHOKE == msg_id:
            return self.handle_choke
        elif ID_UNCHOKE == msg_id:
            return self.handle_unchoke
        elif ID_INTERESTED == msg_id:
            return self.handle_interested
        elif ID_NOT_INTERESTED == msg_id:
            return self.handle_not_interested
        elif ID_HAVE == msg_id:
            return self.handle_have
        elif ID_BITFIELD == msg_id:
            return self.handle_bitfield
        elif ID_REQUEST == msg_id:
            return self.handle_request
        elif ID_PIECE == msg_id:
            return self.handle_piece
        elif ID_CANCEL == msg_id:
            return self.handle_cancel
        elif ID_PORT == msg_id:
            return self.handle_port
        else:
            raise Exception()

    def handle_choke(self, msg_len, payload):
        print 'called handle_choke'

    def handle_unchoke(self, msg_len, payload):
        print 'called handle_unchoke'

    def handle_interested(self, msg_len, payload):
        print 'called handle_interested'

    def handle_not_interested(self, msg_len, payload):
        print 'called handle_not_interested'

    def handle_have(self, msg_len, payload):
        piece_index = self.get_4_byte_to_decimal(payload)
        self.bitfield[piece_index] = True
        print 'called handle_have'

    def handle_bitfield(self, msg_len, payload):
        self.bitfield = BitArray(bytes=payload)
        print 'called handle_bitfield'
        
    def handle_request(self, msg_len, payload):
        print 'called handle_request'

    def handle_piece(self, msg_len, payload):
        index = self.get_4_byte_to_decimal(payload[0:4])
        begin = self.get_4_byte_to_decimal(payload[4:8])
        block = payload[8:]
        dir = '/hackerschool/torrent-client/related_assets/downloads'
        
        filepath = '%s/flag.jpg' % (dir)
        file = open(filepath, 'r+b')
                
        file_pos = index * int(math.pow(2,14)) + begin
        file.seek(file_pos)
        file.write(block)
        file.close()
        
        print 'received index=%d being=%d block_size=%d' % (index, begin, len(block))
        
        
    def handle_cancel(self, msg_len, payload):
        print 'called handle_cancel'
        
        
    def handle_port(self, msg_len, payload):
        print 'called handle_port'
        
        
    def get_interested_message(self):
        # <len=0001><id=2>
        length = BitArray(uint=1, length=32).bytes
        id = chr(ID_INTERESTED)
        
        msg = '%s%s' % (length, id)
        return msg
    
    
    def get_request_piece_message(self, piece_index, begin, requested_length):
        # <len=0013><id=6><index><begin><length>
        length = BitArray(uint=13, length=32).bytes
        id = chr(ID_REQUEST)
        index = BitArray(uint=piece_index, length=32).bytes
        begin = BitArray(uint=begin, length=32).bytes # block offset
        requested_length = BitArray(uint=requested_length, length=32).bytes # block offset
        
        msg = '%s%s%s%s%s' % (length, id, index, begin, requested_length)
        return msg
