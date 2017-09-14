from playground.network.packet.fieldtypes import UINT8, STRING, INT16, BOOL
from playground.network.packet.fieldtypes import BOOL, STRING
from playground.network.packet import PacketType
import playground
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


class ColorServerPro(asyncio.Protocol):
    def __init__(self):
        cid = 1
        message = 'A52A2A'
        self.state = 'none'
        self.id = cid
        self.message = message
        self.r = int(message[:2], 16)
        self.g = int(message[2:4], 16)
        self.b = int(message[4:], 16)
    
    # def findcolor(self, ):
    
    def connection_made(self, transport):
        self.transport = transport
        self.state = 'connected'
        print(self.state)
    
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
                print('color data send:{}'.format(self.message))
            elif isinstance(pkt, Decodepackage) and self.state == 'r_decode':
                print('server: decode color received')
                if pkt.ID == self.id and pkt.value1 == self.r and pkt.value2 == self.g and pkt.value3 == self.b:
                    print('success')
                    packet2 = Resultpackage()
                    packet2.ID = self.id
                    packet2.passfail = True
                    packet2Bytes = packet2.__serialize__()
                    self.state = 'complete'
                    self.transport.write(packet2Bytes)
            else:
                print('server: none expect package matched')


loop = asyncio.get_event_loop()
loop.set_debug(enabled=True)
coro = playground.getConnector().create_playground_server(lambda: ColorServerPro(), 8868)
server = loop.run_until_complete(coro)
print("ColorServer Started at {}".format(server.sockets[0].gethostname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

server.close()
loop.run_until_complete(server.wait_closed())
loop.close()
