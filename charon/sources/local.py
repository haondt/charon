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
    def paths(self) -> list[str]:
        return [self._path]

    @property
    def context(self):
        return self._context

class ManyPathLocalSource:
    def __init__(self, abspaths: list[str]):
        self._paths = abspaths

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return

    @property
    def paths(self) -> list[str]:
        return self._paths

    @property
    def context(self):
        return "."


def create_local_source(config):
    if 'path' in config:
        if 'paths' in config:
            raise ValueError(f'Config cannot have both \'path\' and \'paths\'')
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
    else:
        paths = config['paths']
        paths = [os.path.abspath(p) for p in paths]
        return ManyPathLocalSource(paths)


