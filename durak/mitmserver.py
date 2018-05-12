import asyncio
import json
import sys
import traceback

from command_processors import parse_command, generate_reply_one


class MitmForwarder:
    TIMEOUT = 1

    def __init__(self, reader, writer, overrides=None, logging_prefix=''):
        self.reader = reader
        self.writer = writer
        self.logging_prefix = logging_prefix
        if overrides is None:
            self.overrides = {}
        else:
            self.overrides = overrides
        self._shutdown = False

    def stop(self):
        print('{}: Stop is called'.format(self.logging_prefix))
        self._shutdown = True

    async def forward(self):
        try:
            while not self.reader.at_eof() and not self._shutdown:
                try:
                    line = await asyncio.wait_for(self.reader.readline(),
                                                  timeout=self.TIMEOUT)
                except asyncio.TimeoutError:
                    continue
                print("{}: {}".format(self.logging_prefix,
                                      line.decode('UTF-8').strip()))
                command, command_data = parse_command(line)
                if command in self.overrides:
                    command, command_data = self.overrides[command](
                            command, command_data)
                    line = generate_reply_one(command, command_data)
                    print("{} override: {}".format(
                        self.logging_prefix, line.decode('UTF-8').strip()))
                self.writer.write(line)
            else:
                print("Connection closed")
        except Exception as e:
            traceback.print_exc()


def set_up_proxy(HOST, PORT, loop):
    async def proxy_new_connection(client_reader, client_writer):
        server_reader, server_writer = await asyncio.open_connection(
                REMOTE_HOST,
                REMOTE_PORT,
                loop=loop
        )
        server_to_client_forward = MitmForwarder(
                server_reader,
                client_writer,
                overrides=server_to_client_overrides,
                logging_prefix="Server")
        server_to_client_task = loop.create_task(
                server_to_client_forward.forward())
        client_to_server_forward = MitmForwarder(
                client_reader,
                server_writer,
                overrides=client_to_server_overrides,
                logging_prefix="Client")
        client_to_server_task = loop.create_task(
                client_to_server_forward.forward())
        client_to_server_task.add_done_callback(
                lambda x: server_to_client_forward.stop())
        server_to_client_task.add_done_callback(
                lambda x: client_to_server_forward.stop())
    return proxy_new_connection


def override_update_field(command, command_data):
    if command_data["k"] == "name":
        value = "thebestname"
    elif command_data["k"] == "coins":
        value = 12341341
    elif command_data["k"].startswith("score"):
        value = 123131313
    else:
        value = command_data["v"]
    return command, {"k": command_data["k"], "v": value}


def override_sign_field(command, command_data):
    if "key" in command_data:
        return command, {"key": "haha penis"}
    elif "hash" in command_data:
        return command, {"hash": "penis=="}
    else:
        return command, command_data


def override_create_field(command, command_data):
    new_command = command_data.copy()
    new_command["players"] = 7
    return command, new_command


server_to_client_overrides = {
    'uu': override_update_field,
    'sign': override_sign_field,
}


client_to_server_overrides = {
    'sign': override_sign_field,
    'create': override_create_field,
}


if __name__ == "__main__":
    REMOTE_HOST = sys.argv[1]
    REMOTE_PORT = int(sys.argv[2])
    HOST = sys.argv[3]
    PORT = int(sys.argv[4])
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(set_up_proxy(REMOTE_HOST, REMOTE_PORT, loop),
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
    loop.run_until_complete(server.wait_closed())
    loop.close()
