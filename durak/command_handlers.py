import json
from datetime import datetime

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
               'achc': 1488,
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
