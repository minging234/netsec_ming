from playground.asyncio_lib.testing import TestLoopEx
from playground.network.testing import MockTransportToProtocol
from playground.network.packet.fieldtypes import UINT8, STRING, INT16, BOOL
from playground.network.packet import PacketType
import asyncio


class RequestColorpackage(PacketType):
    DEFINITION_IDENTIFIER = "lab2b.student_xym.Requestcolorpackage"
    DEFINITION_VERSION = "1.0"
    FIELDS = [
]


class ColorCodepackage(PacketType):
    DEFINITION_IDENTIFIER = "lab2b.student_xym.ColorCodepackage"
    DEFINITION_VERSION = "1.0"
    FIELDS = [
              ("ID", UINT8), ("colorcode", STRING)
              ]


class Decodepackage(PacketType):
    DEFINITION_IDENTIFIER = "lab2b.student_xym.Decodepackage"
    DEFINITION_VERSION = "1.0"
    FIELDS = [
              ("ID", UINT8), ("value1", INT16), ("value2", INT16), ("value3", INT16)
              ]


class Resultpackage(PacketType):
    DEFINITION_IDENTIFIER = "lab2b.student_xym.Resultpackage"
    DEFINITION_VERSION = "1.0"
    FIELDS = [
              ("ID", UINT8), ("passfail", BOOL)
              ]


class ClolorClientPro(asyncio.Protocol):
    def __init__(self, loop):
        self.state = 'none'
        self.id = 0
        self.colorcode = 'none'
        self.vlue1 = 0
        self.vlue2 = 0
        self.vlue3 = 0
        self.loop = loop
        self.transport = None
    
    def sendfirst(self):
        packet1 = RequestColorpackage()
        packet1a = packet1.__serialize__()
        self.state = 'r_colorcode'
        self.transport.write(packet1a)
    
    def passcode(self):
        return self.colorcode
    
    def senddecode(self,v1, v2, v3):
        packet1 = Decodepackage()
        packet1.ID = self.id
        packet1.value1 = v1
        packet1.value2 = v2
        packet1.value3 = v3
        packet1bytes = packet1.__serialize__()
        self.transport.write(packet1bytes)
    
    def connection_made(self, transport):
        self.transport = transport
        self.state = 'connected'
    
    def data_received(self, data):
        deserializer = PacketType.Deserializer()
        deserializer.update(data)
        for pkt in deserializer.nextPackets():
            if isinstance(pkt, ColorCodepackage) and self.state == 'r_colorcode':
                print('client: color code received')
                self.colorcode = pkt.colorcode
                self.id = pkt.ID
                # self.value1 = int(pkt.colorcode[:2], 16)
                # self.value2 = int(pkt.colorcode[2:4], 16)
                # self.value3 = int(pkt.colorcode[4:], 16)
                self.state = 'r_result'
            elif isinstance(pkt, Resultpackage) and self.state == 'r_result':
                print('client: pass fail received')
                self.state = 'complete'
            else:
                print('client: none expect package matched')
                self.transport = None
                self.loop.stop()

    def connection_lost(self, exc):
        self.loop.stop()
        self.transport = None
        print('connection lost')


class ColorServerPro(asyncio.Protocol):
    def __init__(self):
        self.state = 'none'
    
    def findcolor(self, cid, message):
        self.id = cid
        self.message = message
        self.r = int(message[:2], 16)
        self.g = int(message[2:4], 16)
        self.b = int(message[4:], 16)
    
    def connection_made(self, transport):
        self.transport = transport
        self.state = 'connected'
        peername = transport.get_extra_info('peername')
        print('Connection from:{}'.format(peername))
    
    def data_received(self, data):
        deserializer = PacketType.Deserializer()
        deserializer.update(data)
        for pkt in deserializer.nextPackets():
            if isinstance(pkt, RequestColorpackage) and self.state == 'connected':
                print('server: color request received')
                packet1 = ColorCodepackage()
                packet1.ID = self.id
                packet1.colorcode = self.message
                packet1bytes = packet1.__serialize__()
                self.state = 'r_decode'
                self.transport.write(packet1bytes)
            # print('color data send')
            elif isinstance(pkt, Decodepackage) and self.state == 'r_decode':
                print('server: decode color received')
                if pkt.ID == self.id and pkt.value1 == self.r and pkt.value2 == self.g and pkt.value3 == self.b:
                    packet2 = Resultpackage()
                    packet2.ID = self.id
                    packet2.passfail = True
                    packet2Bytes = packet2.__serialize__()
                    self.state = 'complete'
                    self.transport.write(packet2Bytes)
            else:
                print('server: none expect package matched')


def basicUnitTest():
    loop = TestLoopEx()
    asyncio.set_event_loop(loop)
    client = ClolorClientPro(loop)
    server = ColorServerPro()
    transportToServer = MockTransportToProtocol(server)
    transportToClient = MockTransportToProtocol(client)
    server.connection_made(transportToClient)
    client.connection_made(transportToServer)
    
    assert server.state == 'connected'
    assert client.state == 'connected'
    
    cid = 1
    message = 'A52A2A'
    server.findcolor(cid, message)
    client.sendfirst()
    
    assert server.state == 'r_decode'
    assert client.state == 'r_result'
    
    colorhex = client.passcode()
    R = int(colorhex[:2], 16)
    G = int(colorhex[2:4], 16)
    B = int(colorhex[4:], 16)
    client.senddecode(R, G, B)
    
    assert server.state == 'complete'
    assert server.state == 'complete'

if __name__ == "__main__":
    basicUnitTest()
