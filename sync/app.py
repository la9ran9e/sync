from . import server


def create_server(bind_address):
    return server.Server(bind_address)
