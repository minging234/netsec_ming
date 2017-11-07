# import asyncio
import heapq
from playground.network.common import StackingProtocol
from playground.network.packet.PacketType import PacketType
from ...playgroundpackets import PEEPPacket, packet_deserialize
from ..transport.PEEPTransport import PEEPTransport


class PEEPClient(StackingProtocol):

    TIMEOUT_SECONDS = 5
    P_WINDOW = 5

    def __init__(self):
        super().__init__()
        self.transport = None
        self._deserializer = PacketType.Deserializer()
        # self._timeout_handler = None
        self._state = 0
        self._sequence_number = 0
        self._other_seq_number = 0
        self._passed_list = []
        self._backlog_list = []
        self._receive_list = []

    def connection_made(self, transport):
        print('---- PEEP client connected ----')
        self.transport = transport
        self.transport.protocol = self
        self.handshake_syn()

    def data_received(self, data):
        self._deserializer.update(data)
        for data_packet in self._deserializer.nextPackets():
            if isinstance(data_packet, PEEPPacket):
                if self._state == 1:
                    if data_packet.Type == 1:
                        # self._timeout_handler.cancel()
                        self.handshake_ack(data_packet)
                        self.higherProtocol().connection_made(PEEPTransport(self.transport, self))
                    else:
                        print('PEEP client is waiting for a SYN-ACK packet.')
                elif self._state == 2:
                    if data_packet.Type == 2:
                        # self._timeout_handler.cancel()
                        self.ack_received(data_packet)
                    elif data_packet.Type == 5:
                        # self._timeout_handler.cancel()
                        self.reorder_packet(data_packet)
                else:
                    raise ValueError('PEEP client wrong state.')
            else:
                print('PEEP client is waiting for a PEEP packet.')

    def connection_lost(self, exc):
        self.higherProtocol().connection_lost(exc)

    def resend(self, state):
        if state == self._state:
            print("should resend")
            self.handshake_syn()

    def handshake_syn(self):
        handshake_packet = PEEPPacket.Create_SYN()
        print('PEEP client sent SYN.')
        self._state = 1
        packet_bytes = handshake_packet.__serialize__()
        self._sequence_number = handshake_packet.SequenceNumber + 1
        self.transport.write(packet_bytes)
        # self._timeout_handler = asyncio.get_event_loop().call_later(PEEPClient.TIMEOUT_SECONDS, self.handshake_syn)

    def handshake_ack(self, data_packet):
        if data_packet.verifyChecksum():
            if data_packet.Acknowledgement == self._sequence_number:
                print('PEEP client received SYN-ACK.')
                self._other_seq_number = data_packet.SequenceNumber + 1
                handshake_packet = PEEPPacket.Create_ACK(self._other_seq_number, self._sequence_number)
                self._state = 2
                print('PEEP client sent ACK')
                self.transport.write(handshake_packet.__serialize__())
                # self._timeout_handler = asyncio.get_event_loop().call_later(PEEPClient.TIMEOUT_SECONDS, self.handshake_ack)
            else:
                print('Incorrect sequence number.')
        else:
            raise ValueError('SYN-ACK incorrect checksum.')

    def pass_packet(self, packet):
        print('pass_packet received packet-------------------------------------------------------')
        if len(self._passed_list) < PEEPClient.P_WINDOW:
            heapq.heappush(self._passed_list, (packet.SequenceNumber, packet))
            self._sequence_number += len(packet.Data)
            print("send packet number is ", packet.SequenceNumber)
            print("the current waiting for reply heap is ", len(self._passed_list))
            self.transport.write(packet.__serialize__())
            # print('pass_packet send packet')
        else:
            # heapq.heappush(self._backlog_list, (packet.SequenceNumber, packet))
            # print('save in the backlog----', packet.SequenceNumber)
            self._backlog_list.append((packet.SequenceNumber, packet))
            print('the backlog package is that ------------------', len(self._backlog_list))

    def send_backlog(self):
        while len(self._passed_list) < 5 and len(self._backlog_list) > 0:
            (seq, packet) = self._backlog_list[0]
            del self._backlog_list[0]
            heapq.heappush(self._passed_list, (seq, packet))
            self._sequence_number += len(packet.Data)
            print('send backlog package -----', packet.SequenceNumber)
            self.transport.write(packet.__serialize__())

    def send_ack(self):
        print('PEEP client send ACK.')
        ack_packet = PEEPPacket.Create_ACK(self._other_seq_number, self._sequence_number)
        self.transport.write(ack_packet.__serialize__())

    def ack_received(self, data_packet):
        if data_packet.verifyChecksum():
            print('PEEP client received data ack packet')
            while self._passed_list[0][0] < data_packet.Acknowledgement:
                heapq.heappop(self._passed_list)
                # self.send_backlog()
                print('the current waiting for reply heap is ', len(self._passed_list))
                print('the current waiting for send heap in the backlog area is ', len(self._backlog_list))
        else:
            print("ack check sum is not valid")

    def reorder_packet(self, data_packet):
        if data_packet.verifyChecksum():
            # print('PEEP client received data packet ---- reorder_packet')
            if data_packet.SequenceNumber == self._other_seq_number:
                self.send_ack()
                self.higherProtocol().data_received(data_packet.Data)
                self._other_seq_number += len(data_packet.Data)
            elif data_packet.SequenceNumber > self._other_seq_number:
                self.send_ack()
                heapq.heappush(self._receive_list, (data_packet.SequenceNumber, data_packet))
                print('push end')

    def ret_sequencenum(self):
        return self._sequence_number


