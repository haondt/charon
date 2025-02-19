import tempfile
import os
import requests
from requests.models import HTTPError

class HttpSource:
    def __init__(self, request: requests.PreparedRequest, filename: str):
        self._request = request
        self._filename = filename
        self._td: tempfile.TemporaryDirectory | None = None

    def __enter__(self):
        self._td = tempfile.TemporaryDirectory()

        response = requests.Session().send(self._request, allow_redirects=False, timeout=30)
        if response.status_code != 200:
            raise HTTPError(f"received status code {response.status_code}")

        path = os.path.join(self._td.name, self._filename)
        with open(path, 'w') as f:
            f.write(response.text)
        return self

    def __exit__(self, *_):
        if self._td is not None:
            try:
                self._td.cleanup()
            finally:
                self._td = None
        return

    @property
    def context(self):
        if self._td is None:
            raise RuntimeError("Cannot provide context when temporary directory is unset.")
        return self._td.name

    @property
    def path(self):
        return "."

def create_http_source(name, config):
    url = config['url']
    headers = {}
    auth = config.get('auth')
    if auth is not None:
        if 'bearer' in auth:
            headers['Authorization'] = f'Bearer {auth["bearer"]}'
    method = config.get('method', 'get')
    extension = config.get('ext', 'txt')
    request = requests.Request(
        method = method.upper(),
        url = url,
        headers = headers
    ).prepare()

    return HttpSource(request, f'{name}.{extension}')
