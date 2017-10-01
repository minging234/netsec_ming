import sys, asyncio
import playground
from playground.network.common.Protocol import StackingProtocol, StackingProtocolFactory, StackingTransport
from playground.network.packet.fieldtypes import UINT8, UINT16, STRING, INT16, BOOL, UINT32, BUFFER
from playground.network.packet.fieldtypes.attributes import Optional
from playground.network.packet import PacketType
from .PEEPTransport import PEEPTransport


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


class PeepPacket(PacketType):
    DEFINITION_IDENTIFIER = "PEEP-Handshake"
    DEFINITION_VERSION = "1.0"

    FIELDS = [

        ("Type", UINT8),

        ("SequenceNumber", UINT32({Optional: True})),

        ("Checksum", UINT16),

        ("Acknowledgement", UINT32({Optional: True})),

        ("Data", BUFFER({Optional: True}))
    ]


class ClolorClientPro(asyncio.Protocol):
    def __init__(self, loop, callback=None):
        self.state = 'none'
        self.id = 0
        self.colorcode = ""
        self.vlue1 = 0
        self.vlue2 = 0
        self.vlue3 = 0
        self.loop = loop
        self.transport = None
        print('client pro init')
        if callback:
            self.callback = callback
        else:
            self.callback = print

    def sendfirst(self):
        packet1 = RequestColorpackage()
        packet1a = packet1.__serialize__()
        self.state = 'r_colorcode'
        self.transport.write(packet1a)
        print('send first app package')

    def setcolorR(self, cdata):
        self.vlue1 = cdata

    def setcolorG(self, cdata):
        self.vlue2 = cdata

    def setcolorB(self, cdata):
        self.vlue3 = cdata

    def connection_made(self, transport):
        self.transport = transport
        self.state = 'connected'
        print('pro make connection')

    def data_received(self, data):
        deserializer = PacketType.Deserializer()
        deserializer.update(data)
        for pkt in deserializer.nextPackets():
            if isinstance(pkt, ColorCodepackage) and self.state == 'r_colorcode':
                self.colorcode = pkt.colorcode
                self.id = pkt.ID
                print('client: color code received :{}'.format(self.colorcode))
                self.state = 'r_result'
                self.loop.add_reader(sys.stdin, control.stdin_R())
                self.loop.add_reader(sys.stdin, control.stdin_G())
                self.loop.add_reader(sys.stdin, control.stdin_B())
                packet1 = Decodepackage()
                packet1.ID = self.id
                packet1.value1 = self.vlue1
                packet1.value2 = self.vlue2
                packet1.value3 = self.vlue3
                packet1bytes = packet1.__serialize__()
                self.transport.write(packet1bytes)
            elif isinstance(pkt, Resultpackage) and self.state == 'r_result':
                print('client: pass fail received')
                self.state = 'complete'
                print(pkt.passfail)
                print(self.state)
            else:
                print('client: none expect package matched')
                self.transport = None
                self.loop.stop()

    def connection_lost(self, exc):
        self.loop.stop()
        self.transport = None
        print('connection lost')


class ColorControl:
    def __init__(self):
        self.txProtocol = None

    def buildProtocol(self, loops):
        return ClolorClientPro(loops, self.callback)

    def connect(self, txProtocol):
        self.txProtocol = txProtocol
        # print("Color Connection to Server Established!")
        self.txProtocol = txProtocol

    def callback(self, message):
        print("Client: {}".format(message))

    def stdin_R(self):
        print("set R value")
        data = sys.stdin.readline()
        if data and data[-1] == "\n":
            data = int(data[:-1])  # strip off \n
        self.txProtocol.setcolorR(data)

    def stdin_G(self):
        print("set G value")
        data = sys.stdin.readline()
        if data and data[-1] == "\n":
            data = int(data[:-1])  # strip off \n
        self.txProtocol.setcolorG(data)

    def stdin_B(self):
        print("set B value")
        data = sys.stdin.readline()
        if data and data[-1] == "\n":
            data = int(data[:-1])  # strip off \n
        self.txProtocol.setcolorB(data)


class PEEPass(StackingProtocol):

    def __init__(self):
        super().__init__()
        self.data = None
        self.transport = None
        self.seqnum = 100
        print('peep pass init')

        # The state is to identify whether the packet type.
        self.state = -1

    def tcpini(self):
        if self.tcpstatus == 'none':
            packet = PeepPacket()
            packet.Type = 0
            packet.SequenceNumber = self.seqnum
            packet.Checksum = 0
            self.state = 0
            print('send SYN package')
            self.transport.write(packet.__serialize__())

    def connection_made(self, transport):
        print('--- peep connect ---')
        self.transport = transport
        self.transport.set_protocol(self)
        print('1 done')
        self.higherProtocol().connection_made(PEEPTransport(self.transport))

    def data_received(self, data):
        print('client peep pass received data')
        deserializer = PacketType.Deserializer()
        deserializer.update(data)
        for pkt in deserializer.nextPackets():
            if isinstance(pkt, PeepPacket):
                if self.state == 1:
                    self.higherProtocol().data_received(data)
                elif pkt.Type == 1 and self.state == 0:
                    print('receive SYN-ACK package')
                    self.state = 1
                    self.seqnum += 1
                    packet = PeepPacket()
                    packet.Type = 2
                    packet.SequenceNumber = self.seqnum
                    packet.Acknowledgement = pkt.SequenceNumber + 1
                    packet.Checksum = 0
                    packet.Data = self.data
                    print('send ACK package')
                    self.transport.write(packet.__serialize__())
                    print('connected')
                else:
                    print('none expect package matched')

    def connection_lost(self, exc):
        self.higherProtocol().connection_lost(exc)

    def process_data(self, data):
        if self.state == -1:
            self.data = data
            self.tcpini()
            print(self.state)
        else:
            self.transport.write(data)


class ClientPass2(StackingProtocol):

    def __init__(self):
        super().__init__
        self.transport = None
        print('pass2 init')

    def connection_made(self, transport):
        print('pass2 connect')
        self.transport = transport
        self.higherProtocol().connection_made(PEEPTransport(self.transport))

    def data_received(self, data):
        print('client pass2 through received data')
        self.higherProtocol().data_received(data)

    def connection_lost(self, exc):
        self.higherProtocol().connection_lost(exc)
        self.transport = None
        print("ps2 con lost")

    def process_data(self, data):
        self.transport.write(data)

 
if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    control = ColorControl()

    f = StackingProtocolFactory(lambda: ClientPass2(),
                                lambda: PEEPass())

    # f = StackingProtocolFactory(lambda: PEEPass(),
    #                             lambda: ClientPass2())

    ptConnector = playground.Connector(protocolStack=f)
    playground.setConnector("pass", ptConnector)

    coro = playground.getConnector('pass').create_playground_connection(lambda : control.buildProtocol(loop),
                                                                        '20174.1.1.1', 8888)

    transport1, protocol = loop.run_until_complete(coro)
    control.connect(protocol)

    protocol.sendfirst()

    loop.run_forever()
    loop.close()


