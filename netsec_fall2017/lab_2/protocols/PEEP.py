import heapq
from playground.network.common import StackingProtocol
from playground.network.packet.PacketType import PacketType

from ..constants import DATA_FIELD_SIZE, WINDOW
from ...playgroundpackets import PEEPPacket

class PEEP(StackingProtocol):

    def __init__(self):
        super(PEEP, self).__init__()
        # transport
        self.transport = None
        # deserializer
        self._deserializer = PacketType.Deserializer()
        # state
        self._state = 0
        # seq num
        self._seq_num_for_handshake = None
        self._seq_num_for_last_packet = None
        self._seq_num_for_next_expected_packet = None
        # heap
        self._retransmission_heap = []
        self._disordered_packets_heap = []
        # size
        self._size_for_last_packet = 1
        # backlog
        self._backlog_buffer = b''

    def ack_received(self, ack_packet):
        print('received ack packet with ack %s' % ack_packet.Acknowledgement)
        if ack_packet.verifyChecksum():
            while len(self._retransmission_heap) > 0 and self._retransmission_heap[0].SequenceNumber < ack_packet.Acknowledgement:
                packet_for_removing = heapq.heappop(self._retransmission_heap)
                print('remove packet from retransmission heap with seq num %s' % packet_for_removing.SequenceNumber)
                if len(self._backlog_buffer) > 0:
                    chunk, self._backlog_buffer = self._backlog_buffer[:DATA_FIELD_SIZE], self._backlog_buffer[DATA_FIELD_SIZE:]
                    data_packet_for_backlog = PEEPPacket.Create_DATA(self._seq_num_for_last_packet, chunk, self._size_for_last_packet)
                    data_packet_for_backlog_bytes = data_packet_for_backlog.__serialize__()
                    self.transport.write(data_packet_for_backlog_bytes)
                    print('sent a data packet from backlog with seq num %s' % data_packet_for_backlog.SequenceNumber)
                    heapq.heappush(self._retransmission_heap, data_packet_for_backlog)
                    self._seq_num_for_last_packet = data_packet_for_backlog.SequenceNumber
                    self._size_for_last_packet = len(data_packet_for_backlog_bytes)
        else:
            print('received a ack packet with incorrect checksum')

    def data_packet_received(self, data_packet):
        print('received data packet with seq num %s' % data_packet.SequenceNumber)
        if data_packet.verifyChecksum():
            if data_packet.SequenceNumber == self._seq_num_for_next_expected_packet:
                # ------ higher protocol data received ------
                self.higherProtocol().data_received(data_packet.Data)
                # -------------------------------------------
                self._seq_num_for_next_expected_packet += len(data_packet.__serialize__())
                # check disordered packets heap whether there exists extra packets can be transmitted
                while len(self._disordered_packets_heap) > 0 and self._disordered_packets_heap[0].SequenceNumber == self._seq_num_for_next_expected_packet:
                    next_packet = heapq.heappop(self._disordered_packets_heap)
                    self.higherProtocol().data_received(next_packet.Data)
                    self._seq_num_for_next_expected_packet += len(next_packet.__serialize__())

            else:
                heapq.heappush(self._disordered_packets_heap, data_packet)
        else:
            print('received a data packet with incorrect checksum')
        # ------ send ack ------
        ack_packet = PEEPPacket.Create_packet_ACK(self._seq_num_for_next_expected_packet)
        self.transport.write(ack_packet.__serialize__())
        print('send ack packet with ack %s' % ack_packet.Acknowledgement)
        # ----------------------

    def process_data(self, data_buffer):
        if len(self._backlog_buffer) > 0:
            self._backlog_buffer += data_buffer
        else:
            while len(data_buffer) > 0 and len(self._retransmission_heap) < WINDOW:
                chunk, data_buffer = data_buffer[:DATA_FIELD_SIZE], data_buffer[DATA_FIELD_SIZE:]
                data_chunk_packet = PEEPPacket.Create_DATA(self._seq_num_for_last_packet or self._seq_num_for_handshake, chunk, self._size_for_last_packet)
                data_chunk_packet_bytes = data_chunk_packet.__serialize__()
                # ------ transport write ------
                self.transport.write(data_chunk_packet_bytes)
                print('sent a data packet with seq num %s' % data_chunk_packet.SequenceNumber)
                # -----------------------------
                heapq.heappush(self._retransmission_heap, data_chunk_packet)
                self._seq_num_for_last_packet = data_chunk_packet.SequenceNumber
                self._size_for_last_packet = len(data_chunk_packet_bytes)

            if len(data_buffer) > 0:
                self._backlog_buffer += data_buffer
                print('backlog buffer length is %s' % len(self._backlog_buffer))
