from playground.asyncio_lib.testing import TestLoopEx
from playground.network.testing import MockTransportToProtocol
from playground.network.packet import PacketType
import asyncio
import packageclass


class ClolorClientPro(asyncio.Protocol):
    def __init__(self,loop):
        self.loop = loop
        self.transport = None
    
    def connection_made(self, transport):
        packet1 = packageclass.RequestColorpackage()
        packet1a = packet1.__serialize__()
        self.transport = transport
        self.transport.write(packet1a)
        print('client: color request sent')
    
    def data_received(self, data):
        deserializer = PacketType.Deserializer()
        deserializer.update(data)
        for pkt in deserializer.nextPackets():
            if isinstance(pkt, packageclass.ColorCodepackage):
                print('client: color code received')
                packet1 = packageclass.Decodepackage()
                packet1.ID = pkt.ID
                packet1.value1 = int(pkt.colorcode[:2], 16)
                packet1.value2 = int(pkt.colorcode[2:4], 16)
                packet1.value3 = int(pkt.colorcode[4:], 16)
                packet1bytes = packet1.__serialize__()
                self.transport.write(packet1bytes)
            # print('decode color send')
            elif isinstance(pkt, packageclass.Resultpackage):
                print('client: pass fail received')
            else:
                print('client: none package matched')

def connection_lost(self, exc):
    self.loop.stop()
        self.transport = None
        print('connection lost')


class ColorServerPro(asyncio.Protocol):
    def __init__(self, cid, message):
        self.id = cid
        self.message = message
        self.r = int(message[:2], 16)
        self.g = int(message[2:4], 16)
        self.b = int(message[4:], 16)
    
    def connection_made(self, transport):
        self.transport = transport
        peername = transport.get_extra_info('peername')
        print('Connection from:{}'.format(peername))
    
    def data_received(self, data):
        deserializer = PacketType.Deserializer()
        deserializer.update(data)
        for pkt in deserializer.nextPackets():
            if isinstance(pkt, packageclass.RequestColorpackage):
                print('server: color request received')
                packet1 = packageclass.ColorCodepackage()
                packet1.ID = self.id
                packet1.colorcode = self.message
                packet1bytes = packet1.__serialize__()
                self.transport.write(packet1bytes)
            # print('color data send')
            elif isinstance(pkt, packageclass.Decodepackage):
                print('server: decode color received')
                if pkt.ID == self.id and pkt.value1 == self.r and pkt.value2 == self.g and pkt.value3 == self.b:
                    packet2 = packageclass.Resultpackage()
                    packet2.ID = self.id
                    packet2.passfail = True
                    packet2Bytes = packet2.__serialize__()
                    self.transport.write(packet2Bytes)
            # print('pass fail status send')
            # self.transport.close()
            else:
                print('server: none package matched')


def basicUnitTest():
    cid = 1
    message = 'A52A2A'
    loop = TestLoopEx()
    asyncio.set_event_loop(loop)
    client = ClolorClientPro(loop)
    server = ColorServerPro(cid, message)
    transportToServer = MockTransportToProtocol(server)
    transportToClient = MockTransportToProtocol(client)
    server.connection_made(transportToClient)
    client.connection_made(transportToServer)

if __name__ == "__main__":
    basicUnitTest()
