from playground.network.common import StackingProtocol, StackingTransport


class PassThroughProtocol(StackingProtocol):

    def __init__(self):
        super().__init__()

    def connection_made(self, transport):
        self.transport = transport
        self.higherProtocol().connection_made(StackingTransport(self.transport))

    def data_received(self, data):
        self.higherProtocol().data_received(data)

    def connection_lost(self, exc):
        self.higherProtocol().connection_lost(exc)

    def process_data(self, data):
        self.transport.write(data)
