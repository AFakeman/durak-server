import asyncio
import json
import sys
import traceback

from command_processors import parse_command, generate_reply_one


class BaseMITMForwarder:
    TIMEOUT = 1

    def __init__(self, reader, writer, logging_prefix=''):
        self.reader = reader
        self.writer = writer
        self.logging_prefix = logging_prefix
        self._shutdown = False

    def stop(self):
        print('{}: Stop is called'.format(self.logging_prefix))
        self._shutdown = True

    @classmethod
    def command_override(cls, command):
        def add_command_to_overrides(func):
            cls.overrides[command] = func
            return func
        return add_command_to_overrides

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


class ClientToServerMITMForwarder(BaseMITMForwarder):
    overrides = {}


class ServerToClientMITMForwarder(BaseMITMForwarder):
    overrides = {}


class MITMProxyServer:
    def __init__(self, REMOTE_HOST, REMOTE_PORT, loop,
                 client_to_server_forward_class=BaseMITMForwarder,
                 server_to_client_forward_class=BaseMITMForwarder):
        self.host = REMOTE_HOST
        self.port = REMOTE_PORT
        self.loop = loop
        self._shutdown = False
        self._tasks = []
        self._forwarders = []
        self.server_to_client_forward_class = server_to_client_forward_class
        self.client_to_server_forward_class = client_to_server_forward_class

    async def handle_new_connection(self, client_reader, client_writer):
        server_reader, server_writer = await asyncio.open_connection(
                self.host,
                self.port,
                loop=self.loop
        )
        server_to_client_forward = self.server_to_client_forward_class(
                server_reader,
                client_writer,
                logging_prefix="Server")
        server_to_client_task = self.loop.create_task(
                server_to_client_forward.forward())
        client_to_server_forward = self.client_to_server_forward_class(
                client_reader,
                server_writer,
                logging_prefix="Client")
        client_to_server_task = self.loop.create_task(
                client_to_server_forward.forward())
        client_to_server_task.add_done_callback(
                lambda x: server_to_client_forward.stop())
        server_to_client_task.add_done_callback(
                lambda x: client_to_server_forward.stop())
        self._tasks.append(client_to_server_task)
        self._tasks.append(server_to_client_task)
        self._forwarders.append(client_to_server_forward)
        self._forwarders.append(server_to_client_forward)

    def stop(self):
        self._shutdown = False
        for forwarder in self._forwarders:
            forwarder.stop()

    async def wait_closed(self):
        for task in self._tasks:
            asyncio.wait(task)


@ServerToClientMITMForwarder.command_override('uu')
def override_update_field(command, command_data):
    if command_data["k"] == "name":
        value = "MITM Successful"
    elif command_data["k"] == "coins":
        value = 13371337
    elif command_data["k"].startswith("score"):
        value = 13371337
    else:
        value = command_data["v"]
    return command, {"k": command_data["k"], "v": value}


@ClientToServerMITMForwarder.command_override('sign')
@ServerToClientMITMForwarder.command_override('sign')
def override_sign_field(command, command_data):
    if "key" in command_data:
        return command, {"key": ""}
    elif "hash" in command_data:
        return command, {"hash": ""}
    else:
        return command, command_data
