import asyncio
import playground
from playground.network.common.Protocol import StackingProtocol, StackingProtocolFactory, StackingTransport
from playground.network.packet.fieldtypes import UINT8, STRING, INT16, BOOL
from playground.network.packet import PacketType


class RequestColorpackage(PacketType):
    DEFINITION_IDENTIFIER = "lab2b.student_xym.Requestcolorpackage"
    DEFINITION_VERSION = "1.3"
    FIELDS = [
]


class ColorCodepackage(PacketType):
    DEFINITION_IDENTIFIER = "lab2b.student_xym.ColorCodepackage"
    DEFINITION_VERSION = "1.3"
    FIELDS = [
              ("ID", UINT8), ("colorcode", STRING)
              ]


class Decodepackage(PacketType):
    DEFINITION_IDENTIFIER = "lab2b.student_xym.Decodepackage"
    DEFINITION_VERSION = "1.3"
    FIELDS = [
              ("ID", UINT8), ("value1", INT16), ("value2", INT16), ("value3", INT16)
              ]


class Resultpackage(PacketType):
    DEFINITION_IDENTIFIER = "lab2b.student_xym.Resultpackage"
    DEFINITION_VERSION = "1.3"
    FIELDS = [
              ("ID", UINT8), ("passfail", BOOL)
              ]


class ColorServerPro(asyncio.Protocol):
    def __init__(self):
        print('color server init')
        cid = 1
        message = 'A52A2A'
        self.state = 'none'
        self.transport = None
        self.id = cid
        self.message = message
        self.r = int(message[:2], 16)
        self.g = int(message[2:4], 16)
        self.b = int(message[4:], 16)
    
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
                print(pkt.ID, pkt.value1, pkt.value2, pkt.value3)
                print(self.id, self.r, self.g, self.b)
                packet2 = Resultpackage()
                packet2.ID = self.id
                if pkt.ID == self.id and pkt.value1 == self.r and pkt.value2 == self.g and pkt.value3 == self.b:
                    print('Server: success, passfail send')
                    packet2.passfail = True
                else:
                    print('Server: fail, passfail send')
                    packet2.passfail = False
                self.state = 'complete'
                self.transport.write(packet2.__serialize__())
            else:
                print('server: none expect package matched')


class ServerPass1(StackingProtocol):
    def __init__(self):
        super().__init__
        print('pass1 init')
    
    def connection_made(self, transport):
        print('pass1 connect')
        self.transport = transport
        self.higherProtocol().connection_made(StackingTransport(self.transport))
    
    def data_received(self, data):
        print('pass1 receive data')
        self.higherProtocol().data_received(data)
    
    def connection_lost(self, exc):
        print("ps1 con lost")
        self.transport.close()
        self.higherProtocol().transport.close()



class ServerPass2(StackingProtocol):
    def __init__(self):
        super().__init__
        print('pass2 init')
    
    def connection_made(self, transport):
        print('pass2 connect')
        self.transport = transport
        self.higherProtocol().connection_made(StackingTransport(self.transport))
    
    def data_received(self, data):
        print('pass2 receive data')
        self.higherProtocol().data_received(data)
    
    def connection_lost(self, exc):
        print("ps2 con lost")
        self.transport.close()
        self.higherProtocol().transport.close()


if __name__ == "__main__":
    
    loop = asyncio.get_event_loop()
    f = StackingProtocolFactory(lambda: ServerPass1(),
                                lambda: ServerPass2())
        
                                ptConnector = playground.Connector(protocolStack=f)
                                playground.setConnector("passthrough", ptConnector)
                                coro = playground.getConnector('passthrough').create_playground_server(lambda : ColorServerPro(), 888)
                                
                                server = loop.run_until_complete(coro)
                                print("ColorServer Started at {}".format(server.sockets[0].gethostname()))
                                try:
                                    loop.run_forever()
                                except KeyboardInterrupt:
                                    pass

    server.close()
    loop.close()
