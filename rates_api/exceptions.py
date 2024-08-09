class PortOrRegionNotFoundException(Exception):
    def __init__(self, port_name: str):
        self.port_name = port_name
