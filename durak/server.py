import json
from datetime import datetime
import socketserver
import sys


def generate_reply_one(command, data=None):
    if data is None:
        encoded = ''
    else:
        encoded = json.dumps(data)
    return (command + encoded + '\n').encode('UTF-8')


def generate_reply(commands):
    if type(commands) is tuple:
        return generate_reply(*commands)
    encoded_commands = []
    for command, data in commands:
        encoded_commands.append(generate_reply_one(command, data))
    return b''.join(encoded_commands)


command_handlers = {}


def command_handler(command):
    def wrapper(func):
        command_handlers[command] = func
        return func
    return wrapper


@command_handler('c')
def command_connect(data):
    response = {"key": "1337"}
    return [('sign', response)]


@command_handler('sign')
def command_sign(data):
    return [('confirmed', None)]


@command_handler('gb')
def command_gb(data):
    return [('gl', {
               'g': [
                   {
                       'id': 0,
                       'p': 2,
                       'cp': 1,
                       'pr': False,
                       'name': "haha benis",
                       'bet': 115,
                       'pc': 0,
                       'deck': 24,
                       'nb': True,
                       'sw': True,
                       'ch': False,
                       'fast': False
                   }
               ]
           })]


def server_reply():
    time = datetime.now().isoformat(timespec='milliseconds') + 'Z'
    srv_id = 'u0'
    return [('server', {'time': time, 'id': srv_id})]


def authorized_reply():
    return [('authorized', {'id': 122345})]


def update_reply(key, value):
    return [('uu', {'k': key, 'v': value})]


def update_many_fields(values):
    reply = []
    for key in values:
        reply += update_reply(key, values[key])
    return reply


@command_handler('auth')
def command_auth(data):
    return server_reply() + \
           authorized_reply() + \
           update_many_fields({
               'name': 'артеммудак',
               'avatar': None,
               'rid': 'asdfsdf',
               'news': False,
               'pw': 0,
               'friends_count': 0,
               'new_msg': False,
               'assets': [7],
               'assel': [7],
               'frame': 'frame_classic',
               'smile': 'smile_classic',
               'shirt': 'shirt_classic',
               'ach': [251731971, 1073745667],
               'achc': 14,
               'achsel': [2, 0],
               'achieve': 'win_pts_1000',
               'coins': 100,
               'wins_s': 45,
               'wins': 483,
               'points_win': 0,
               'points_win_s': 0,
               'points': 0,
               'score': 0,
               'score_s': 0,
               'dtp': r'2016-12-26T12:11:54.726Z',
               'dtfp': r'2017-05-29T17:48:50.090Z',
           })


def handle_command(command, command_data):
    if command in command_handlers:
        return command_handlers[command](command_data)
    else:
        print("Unknown command: " + command)
        return []


class DurakTCPHandler(socketserver.StreamRequestHandler):

    def handle(self):
        print("handle")
        for line in self.rfile:
            line = line.decode('UTF-8')
            if line == '\n':
                print("Empty message received")
                continue
            line = line.rstrip('\n')
            json_idx = line.find('{')
            if json_idx == -1:
                command = line
                command_data = None
            else:
                command = line[:json_idx]
                command_data = json.loads(line[json_idx:])
            print(command)
            print(command_data)
            reply = handle_command(command, command_data)
            encoded_reply = generate_reply(reply)
            self.wfile.write(encoded_reply)


if __name__ == "__main__":
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])

    server = socketserver.TCPServer((HOST, PORT), DurakTCPHandler)

    server.serve_forever()
