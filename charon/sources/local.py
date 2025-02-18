import os

class LocalSource:
    def __init__(self, context: str|None, path: str):
        self._path = path
        self._context = context

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return

    @property
    def path(self):
        return self._path

    @property
    def context(self):
        return self._context

def create_local_source(config):
    path = config['path']
    path = os.path.abspath(path)
    if os.path.isdir(path):
        context = path
        path = '.'
    elif os.path.isfile(path):
        context = os.path.dirname(path)
        path = os.path.basename(path)
    else:
        raise ValueError(f"Invalid path: {path}")

    return LocalSource(context, path)
