import asyncio
from datetime import datetime
import json
import sys

from command_processors import parse_command, generate_reply


class BaseDurakServer:
    TIMEOUT = 1

    @classmethod
    def command_handler(cls, command):
        def add_command_to_handlers(func):
            cls.handlers[command] = func
            return func
        return add_command_to_handlers

    def __init__(self):
        self._shutdown = False

    async def handle_new_connection(self, reader, writer):
        while not reader.at_eof() and not self._shutdown:
            try:
                line = await asyncio.wait_for(reader.readline(),
                                              timeout=self.TIMEOUT)
            except asyncio.TimeoutError:
                continue
            command, command_data = parse_command(line)
            print("Client: {}".format(line.decode('UTF-8').strip()))
            if command == '' and command_data is None:
                continue
            try:
                reply = self.handle_command(command, command_data)
            except NotImplementedError:
                print("Server: [skipping unknown command]")
                continue
            encoded_reply = generate_reply(reply)
            print("Server: {}".format(encoded_reply.decode('UTF-8').strip()))
            writer.write(encoded_reply)

    def handle_command(self, command, command_data):
        if command in self.handlers:
            return self.handlers[command](command, command_data)
        else:
            raise NotImplementedError()

    def stop(self):
        self._shutdown = False

    async def wait_closed(self):
        pass


class DurakServer(BaseDurakServer):
    handlers = {}

    def server_reply():
        time = datetime.now().isoformat(timespec='milliseconds') + 'Z'
        srv_id = 'u0'
        return [('server', {'time': time, 'id': srv_id})]

    @staticmethod
    def authorized_reply():
        return [('authorized', {'id': 123456})]

    @staticmethod
    def update_reply(key, value):
        return [('uu', {'k': key, 'v': value})]

    @staticmethod
    def update_many_fields(values):
        reply = []
        for key in values:
            reply += DurakServer.update_reply(key, values[key])
        return reply


@DurakServer.command_handler('c')
def command_connect(command, data):
    response = {"key": ""}
    return [('sign', response)]


@DurakServer.command_handler('sign')
def command_sign(command, data):
    return [('confirmed', None)]


@DurakServer.command_handler('gb')
def command_gb(command, data):
    return [('gl', {
               'g': [
                   {
                       'id': 0,
                       'p': 2,
                       'cp': 1,
                       'pr': False,
                       'name': "A Mock Game",
                       'bet': 1377,
                       'pc': 0,
                       'deck': 36,
                       'nb': True,
                       'sw': True,
                       'ch': False,
                       'fast': False
                   }
               ]
           })]


@DurakServer.command_handler('auth')
def command_auth(command, data):
    return DurakServer.server_reply() + \
           DurakServer.authorized_reply() + \
           DurakServer.update_many_fields({
               'name': 'Custom Durak',
               'avatar': None,
               'rid': '',
               'news': False,
               'pw': 0,
               'friends_count': 0,
               'new_msg': False,
               'assets': [7],
               'assel': [7],
               'frame': 'frame_classic',
               'smile': 'smile_classic',
               'shirt': 'shirt_classic',
               'ach': [0, 0],
               'achc': 0,
               'achsel': [0, 0],
               'achieve': 'win_pts_1000',
               'coins': 100,
               'wins_s': 0,
               'wins': 0,
               'points_win': 0,
               'points_win_s': 0,
               'points': 0,
               'score': 0,
               'score_s': 0,
               'dtp': r'1970-01-01T00:00:00.000Z',
               'dtfp': r'1970-01-01T00:00:00.000Z',
           })
