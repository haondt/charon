import tempfile
import os
import jq, json
import requests
from requests.models import HTTPError
from typing import Callable

class HttpSource:
    def __init__(self, reqs: list[tuple[requests.PreparedRequest, str, Callable[[str], str]]]):
        self._requests = reqs
        self._td: tempfile.TemporaryDirectory | None = None

    def __enter__(self):
        self._td = tempfile.TemporaryDirectory()

        for req, filename, transformation in self._requests:
            response = requests.Session().send(req, allow_redirects=False, timeout=30)
            if response.status_code != 200:
                raise HTTPError(f"received status code {response.status_code} from url {req.url}")
            text = transformation(response.text) 
            path = os.path.join(self._td.name, filename)
            with open(path, 'w') as f:
                f.write(text)
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
    def paths(self) -> list[str]:
        return ["."]

def create_http_source(name, config):
    targets = []

    if 'url' in config:
        targets.append(prepare_http_source(name, config))

    if 'targets' in config:
        for k, v in config['targets'].items():
            targets.append(prepare_http_source(k, v))

    return HttpSource(targets)

def prepare_http_source(name, config):
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

    transforms = config.get('transform', [])
    if len(transforms) == 0:
        transform = lambda x: x
    else:
        def inner(x: str):
            nonlocal transforms
            for t in  transforms:
                if 'jq' in t:
                    x = json.dumps(jq.compile(t['jq']).input_value(json.loads(x)).first())
            return x
        transform = inner

    return (request, f"{name}.{extension}", transform)

