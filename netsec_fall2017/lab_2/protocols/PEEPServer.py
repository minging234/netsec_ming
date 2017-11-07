import asyncio
import heapq
from playground.network.common import StackingProtocol
from ...playgroundpackets import PEEPPacket
from ..transport import PEEPTransport
from playground.network.packet import PacketType


class PEEPServer(StackingProtocol):

    TIMEOUT_SECONDS = 5
    P_WINDOW = 5

    def __init__(self):
        super().__init__()
        self.transport = None
        self._deserializer = PacketType.Deserializer()
        self._timeout_handler = None
        self._sequence_number = None
        self._state = 0
        self._sequence_number = 0
        self._expect_seq_number = 0
        self._passed_list = []
        self._backlog_list = []
        self._receive_list = []

    def connection_made(self, transport):
        print('---- PEEP server connected ----')
        self.transport = transport

    def data_received(self, data):
        self._deserializer.update(data)
        for data_packet in self._deserializer.nextPackets():
            if isinstance(data_packet, PEEPPacket):
                if self._state == 0:
                    if data_packet.Type == 0:
                        self.handshake_synack(data_packet)
                        self._timeout_handler = asyncio.get_event_loop().call_later(PEEPServer.TIMEOUT_SECONDS, self.forcefully_termination)
                    else:
                        print('PEEP server is waiting for a SYN packet')
                elif self._state == 1:
                    if data_packet.Type == 2:
                        self._timeout_handler.cancel()
                        self.higher_protocol_connection_made(data_packet)
                    else:
                        print('PEEP server is waiting for a ACK packet')
                elif self._state == 2:
                    # print('data_received received data')
                    if data_packet.Type == 5:
                        self.reorder_packet(data_packet)
                    elif data_packet.Type == 2:
                        self.ack_received(data_packet)
                    else:
                        print('not expect package in transmission')

                else:
                    raise ValueError('PEEP server wrong state')
            else:
                print('PEEP server is waiting for a PEEP packet')

    def connection_lost(self, exc):
        self.higherProtocol().connection_lost(exc)

    def handshake_synack(self, data_packet):
        if data_packet.verifyChecksum():
            print('PEEP server received SYN.')
            self._expect_seq_number = data_packet.SequenceNumber + 1
            handshake_packet = PEEPPacket.Create_SYN_ACK(data_packet.SequenceNumber)
            self._sequence_number = handshake_packet.SequenceNumber + 1
            self._state = 1
            self.transport.write(handshake_packet.__serialize__())
            print('PEEP server sent SYN-ACK')
        else:
            print('SYN incorrect checksum.')

    def higher_protocol_connection_made(self, data_packet):
        if data_packet.verifyChecksum():
            if data_packet.Acknowledgement == self._sequence_number:
                print('PEEP Server received ACK')
                self._state = 2
                self.higherProtocol().connection_made(PEEPTransport(self.transport, self))
            else:
                print('Incorrect sequence number.')
        else:
            print('ACK incorrect checksum')

    def pass_packet(self, packet):
        # print('Server: pass_packet received packet')
        if len(self._passed_list) < PEEPServer.P_WINDOW:
            packet_bytes = packet.__serialize__()
            self._sequence_number += len(packet.Data)
            heapq.heappush(self._passed_list, (packet.SequenceNumber, packet))
            self.transport.write(packet_bytes)
            # print('Server: pass_packet send packet')
        else:
            heapq.heappush(self._backlog_list, (packet.SequenceNumber, packet))

    def send_backlog(self):
        while len(self._passed_list) < 5 and len(self._backlog_list) > 0:
            (seq, packet) = heapq.heappop(self._backlog_list)
            heapq.heappush(self._passed_list, (packet.SequenceNumber, packet))
            self._sequence_number += len(packet.Data)
            self.transport.write(packet.__serialize__())

    def send_ack(self, expect, seq):
        print('PEEP server send ACK,','the expect Sequence number is ', expect)
        ack_packet = PEEPPacket.Create_ACK(expect, seq)
        self.transport.write(ack_packet.__serialize__())

    def ack_received(self, data_packet):
        if data_packet.verifyChecksum():
            print('PEEP server received data ack packet')
            while self._passed_list[0] < data_packet.Acknowledgement:
                heapq.heappop(self._passed_list)
                self.send_backlog()
        else:
            print("ack check sum is not valid")

    def reorder_packet(self, data_packet):
        if data_packet.verifyChecksum():
            if data_packet.SequenceNumber == self._expect_seq_number:
                self._expect_seq_number += len(data_packet.Data)
                print("the sequence number of data is ", data_packet.SequenceNumber)
                print("the data received is ", data_packet.Data)
                # self.higherProtocol().data_received(data_packet.Data)
                self.send_ack(self._expect_seq_number, self._sequence_number)
            elif data_packet.SequenceNumber > self._expect_seq_number:
                self.send_ack(self._expect_seq_number, self._sequence_number)
                heapq.heappush(self._receive_list, (data_packet.SequenceNumber, data_packet))
                print('data_packet.SequenceNumber > self._expect_seq_number')
                print(data_packet.SequenceNumber,self._expect_seq_number)
            else:
                print('received a packet again')

    def ret_sequencenum(self):
        return self._sequence_number

    def forcefully_termination(self):
        print('Timeout session')
        self.transport.close()
