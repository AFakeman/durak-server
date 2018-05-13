import asyncio
import sys

from durak_server import DurakServer
from mitm_server import (
        MITMProxyServer,
        ClientToServerMITMForwarder,
        ServerToClientMITMForwarder,
)


def create_durak_server():
    return DurakServer()


def create_mitm_server(REMOTE_HOST, REMOTE_PORT, loop=None):
    return MITMProxyServer(
                REMOTE_HOST, REMOTE_PORT, loop,
                client_to_server_forward_class=ClientToServerMITMForwarder,
                server_to_client_forward_class=ServerToClientMITMForwarder
            )


if __name__ == "__main__":
    MODE = sys.argv[1]
    HOST = sys.argv[2]
    PORT = int(sys.argv[3])

    if len(sys.argv) > 4:
        argv_rest = sys.argv[4:]
    else:
        argv_rest = []

    loop = asyncio.get_event_loop()

    if MODE == 'durak':
        handler_object = create_durak_server()
    elif MODE == 'mitm':
        handler_object = create_mitm_server(*argv_rest, loop=loop)
    else:
        raise NotImplementedError("No server for mode: {}".format(MODE))

    coro = asyncio.start_server(handler_object.handle_new_connection,
                                HOST, PORT, loop=loop)
    server = loop.run_until_complete(coro)

    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    server.close()
    handler_object.stop()
    loop.run_until_complete(server.wait_closed())
    loop.run_until_complete(handler_object.wait_closed())
    loop.close()
