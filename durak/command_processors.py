import json


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


def parse_command(raw_line):
    line = raw_line.decode('UTF-8').rstrip('\n')
    json_idx = line.find('{')
    if json_idx == -1:
        command = line
        command_data = None
    else:
        command = line[:json_idx]
        command_data = json.loads(line[json_idx:])
    return command, command_data
