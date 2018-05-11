"""
This example shows how to send a reply from the proxy immediately
without sending any data to the remote server.
"""
from mitmproxy import http
import os

content_types = {
    ".png": "image/png",
    ".json": "application/json",
    ".html": "text/html",
}

STATIC_DIR = 'static'


def request(flow: http.HTTPFlow) -> None:
    relative_path = flow.request.path.split('?')[0].lstrip('/')
    _, extension = os.path.splitext(relative_path)

    file_path = os.path.join(STATIC_DIR, relative_path)

    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            file_contents = f.read()
        flow.response = http.HTTPResponse.make(
            200,  # (optional) status code
            file_contents,  # (optional) content
            {"Content-Type": content_types[extension]}  # (optional) headers
        )
