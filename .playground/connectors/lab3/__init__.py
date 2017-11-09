import playground
from netsec_fall2017.lab_3.factory.ProtocolFactory import get_lab3_client_factory, get_lab3_server_factory


cf = get_lab3_client_factory()
sf = get_lab3_server_factory()
lab3_connector = playground.Connector(protocolStack=(cf, sf))
playground.setConnector('lab3_protocol', lab3_connector)
