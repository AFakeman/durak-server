from http.server import BaseHTTPRequestHandler, HTTPServer
from http.client import parse_headers
import os.path
from shutil import copyfileobj
import sys
from urllib.parse import urlparse, urlunparse
from urllib.request import urlopen


filetypes = {
        'json': 'application/json',
        'jpg': 'image/jpeg',
        'png': 'image/png',
}


class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.protocol_version = 'HTTP/1.1'
        host = self.headers["Host"]
        path_split = urlparse(self.path)
        path = path_split.path.lstrip('/')
        query = path_split.query
        url = urlunparse(
                ("http", host, path, '', query, '')
        )
        self.send_response(200)
        self.end_headers()
        print(path)
        local_path = os.path.join('static', path)
        if os.path.exists(local_path):
            print("Using local file...")
            with open(local_path, 'rb') as f:
                copyfileobj(f, self.wfile)
        else:
            print("Using remote file...")
            copyfileobj(urlopen(url), self.wfile)


def run(host, port, server_class=HTTPServer,
        handler_class=ProxyHTTPRequestHandler):
    server_address = (host, port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


if __name__ == "__main__":
    host = sys.argv[1]
    port = int(sys.argv[2])
    run(host, port)
