import asyncio
import json
import sys

from command_handlers import handle_command, generate_reply
from command_processors import parse_command


async def DurakTCPHandler(reader, writer):
    while not reader.at_eof():
        line = await reader.readline()
        command, command_data = parse_command(line)
        if line == '' and command_data is None:
            print("Empty message received")
            continue
        print(command)
        print(command_data)
        reply = handle_command(command, command_data)
        encoded_reply = generate_reply(reply)
        writer.write(encoded_reply)


if __name__ == "__main__":
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])

    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(DurakTCPHandler, HOST, PORT, loop=loop)
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
