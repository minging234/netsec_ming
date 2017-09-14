from playground.network.packet.fieldtypes import UINT8, STRING, INT16, BOOL
from playground.network.packet.fieldtypes import BOOL, STRING
from playground.network.packet import PacketType
import playground
import sys, time, os, logging, asyncio

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
    def __init__(self, loop, callback=None):
        self.state = 'none'
        self.id = 0
        self.colorcode = ""
        self.vlue1 = 0
        self.vlue2 = 0
        self.vlue3 = 0
        self.loop = loop
        self.transport = None
        
        if callback:
            self.callback = callback
        else:
            self.callback = print

def sendfirst(self):
    packet1 = RequestColorpackage()
        packet1a = packet1.__serialize__()
        self.state = 'r_colorcode'
        self.transport.write(packet1a)

    def setcolorR(self, cdata):
        self.vlue1 = cdata

def setcolorG(self, cdata):
    self.vlue2 = cdata
    
    def setcolorB(self, cdata):
        self.vlue2 = cdata
        packet1 = Decodepackage()
        packet1.ID = self.id
        packet1.value1 = self.vlue1
        packet1.value2 = self.vlue2
        packet1.value3 = self.vlue3
        packet1bytes = packet1.__serialize__()
        self.transport.write(packet1bytes)
    
    def connection_made(self, transport):
        self.transport = transport
        self.state = 'connected'
        print('make connection')
    
    def data_received(self, data):
        deserializer = PacketType.Deserializer()
        deserializer.update(data)
        for pkt in deserializer.nextPackets():
            if isinstance(pkt, ColorCodepackage) and self.state == 'r_colorcode':
                print('client: color code received')
                self.colorcode = pkt.colorcode
                self.id = pkt.ID
                self.state = 'r_result'
                print(self.colorcode)
            elif isinstance(pkt, Resultpackage) and self.state == 'r_result':
                print('client: pass fail received')
                self.state = 'complete'
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
        print("Color Connection to Server Established!")
        self.txProtocol = txProtocol
        print("Enter Message: ", end="")
    
    def callback(self, message):
        print("Server Response: {}".format(message))
    
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


control = ColorControl()
loop = asyncio.get_event_loop()
loop.set_debug(enabled=True)
coro = playground.getConnector().create_playground_connection (lambda :control.buildProtocol(loop), '20174.1.1.1', 8868)

transport, protocol = loop.run_until_complete(coro)

control.connect(protocol)
protocol.sendfirst()


loop.add_reader(sys.stdin, control.stdin_R())
loop.add_reader(sys.stdin, control.stdin_G())
loop.add_reader(sys.stdin, control.stdin_B())


loop.run_forever()
loop.close()

