from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import UINT8, STRING, INT16, BOOL


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


def basicUnitTest():
    
    packet1 = RequestColorpackage()
    packet1Bytes = packet1.__serialize__()
    packet1a = RequestColorpackage.Deserialize(packet1Bytes)
    if packet1 == packet1a:
        print("these two RequestColorpackage are same")
    else:
        print('wrong')
    
    packet2 = ColorCodepackage()
    packet2.ID = 1
    packet2.colorcode = "A52A2A"
    packet2Bytes = packet2.__serialize__()
    packet2a = ColorCodepackage.Deserialize(packet2Bytes)
    if packet2 == packet2a:
        print("these two ColorCodepackage are same")
    else:
        print('wrong')
    
    packet3 = Decodepackage()
    packet3.ID = 1
    packet3.value1 = 105
    packet3.value2 = 100
    packet3.value3 = 0
    packet3Bytes = packet3.__serialize__()
    packet3a = Decodepackage.Deserialize(packet3Bytes)
    if packet3 == packet3a :
        print("these two Decodepackage are same")
    else:
        print('wrong')
    
    packet4 = Resultpackage()
    packet4.ID = 3
    packet4.passfail = True
    packet4Bytes = packet4.__serialize__()
    packet4a = Resultpackage.Deserialize(packet4Bytes)
    if packet4a == packet4 :
        print("these two Resultpackage are same")
    else:
        print("wrong")
    
    pstream = packet1Bytes + packet2Bytes + packet3Bytes + packet4Bytes
    deserializer = PacketType.Deserializer()
    deserializer.update(pstream)
    for pkt in deserializer.nextPackets():
        if isinstance(pkt,RequestColorpackage): print('color request')
        elif isinstance(pkt, ColorCodepackage): print('color code')
        elif isinstance(pkt, Decodepackage): print('decode color')
        elif isinstance(pkt, Resultpackage): print('pass fail')
        else: print("none")

if __name__ == "__main__":
    basicUnitTest()

