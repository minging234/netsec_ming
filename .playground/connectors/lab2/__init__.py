import playground
from netsec_fall2017.lab_2.factory.PEEPFactory import get_lab2_client_factory, get_lab2_server_factory


cf = get_lab2_client_factory()
sf = get_lab2_server_factory()
lab2_connector = playground.Connector(protocolStack=(cf, sf))

playground.setConnector('lab2_protocol', lab2_connector)


