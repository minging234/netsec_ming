import asyncio
import playground
from playground.network.common.Protocol import StackingProtocol, StackingProtocolFactory, StackingTransport


class clienpo(asyncio.Protocol):
    def __init__(self):
        # self.loop = loop
        self.transport = None
        print('pro init')
    
    def connection_made(self, transport):
        print('connection made')
        self.transport = transport
        transport.write(b'hello')
        print('Data sent')
    
    def data_received(self, data):
        print('data received: '.format(data.decode()))
    
    def connection_lost(self, exc):
        # self.loop.stop()
        print('pro connect lost')


if __name__ == "__main__":
    
    loop = asyncio.get_event_loop()
    
    # f = StackingProtocolFactory(lambda: clienpass(),lambda: serpass())
    
    # ptConnector = playground.Connector(protocolStack=f)
    # playground.setConnector("passthrough", ptConnector)
    
    coro = playground.getConnector().create_playground_connection(lambda: clienpo(), '20174.1.1.1', 8885)
    
    loop.run_until_complete(coro)
    loop.close()
