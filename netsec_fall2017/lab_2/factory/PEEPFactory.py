from playground.network.common import StackingProtocolFactory
from ..protocols import PEEPServer, PEEPClient, PassThroughProtocol


def get_server_factory():
    return StackingProtocolFactory(lambda: PassThroughProtocol(), lambda: PEEPServer())


def get_client_factory():
    return StackingProtocolFactory(lambda: PassThroughProtocol(), lambda: PEEPClient())