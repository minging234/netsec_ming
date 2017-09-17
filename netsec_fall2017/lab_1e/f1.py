import asyncio
import playground
from playground.network.common.Protocol import StackingProtocol, StackingProtocolFactory, StackingTransport
import sys, time, os, logging, asyncio


class serpo(asyncio.Protocol):
    def __init__(self):
        self.transport = None
    
    def connection_made(self, transport):
        print('pro made a connection')
        self.transport = transport
    
    def data_received(self, data):
        print('pro receive data')
        print(data)


class serpass1(StackingProtocol):
    def __init__(self):
        super.__init__()
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


class serpass2(StackingProtocol):
    def __init__(self):
        super.__init__()
        print('pass2 init')
    
    def connection_made(self, transport):
        print('pass2 connect')
        self.transport = transport
        self.higherProtocol().connection_made(StackingTransport(self.transport))
    
    def data_received(self, data):
        print('pass2 receive data')
        self.higherProtocol().data_received(data)
    
    def connection_lost(self, exc):
        print("ps1 con lost")
        self.transport.close()
        self.higherProtocol().transport.close()




if __name__ == "__main__":
    
    # loop = asyncio.get_event_loop()
    #
    # f = StackingProtocolFactory(lambda: serpass1(), lambda: serpass2())
    #
    # ptConnector = playground.Connector(protocolStack=f)
    # playground.setConnector("passthrough", ptConnector)
    #
    # coro = playground.getConnector('passthrough').create_playground_server(lambda: serpo(), 8885)
    #
    # server = loop.run_until_complete(coro)
    #
    # print('serving on')
    # try:
    #     loop.run_forever()
    # except KeyboardInterrupt:
    #     pass
    #
    # server.close()
    
    loop = asyncio.get_event_loop()
    
    f = StackingProtocolFactory(lambda: serpass1(), lambda: serpass2())
    ptConnector = playground.Connector(protocolStack=f)
    playground.setConnector('passthrough', ptConnector)
    coro = playground.getConnector('passthrough').create_playground_server(lambda: serpo(), 8885)
    
    # coro = playground.getConnector().create_playground_server(lambda: serpo(), 8886)
    
    server = loop.run_until_complete(coro)
    print('serving on')
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    server.close()
    loop.close()
