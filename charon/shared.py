import yaml
import logging
from . import sources
from . import restic

_logger = logging.getLogger(__name__)

def load_config(config_file):
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)

def get_task(name, config):
    source = config['source']
    repo_config = config['repository']

    source_type = source['type']
    if source_type == "local":
        source_factory = lambda: sources.local.create_local_source(source)
    # elif source_type == "http":
    #     source_factory = sources.http.create_http_source(name, source)
    # elif source_type == "sqlite":
    #     TODO
    else:
        raise KeyError(f'unknown source type: {source_type}')

    repo = restic.get_repository(repo_config)

    def inner():
        nonlocal source_factory
        nonlocal repo
        with source_factory() as source:
            if (repo_config.get('create', True)):
                if not repo.exists():
                    _logger.info(f'[{name}] initializing repository')
                    repo.init_repo()

            _logger.info(f'[{name}] creating snapshot')
            repo.backup([source.path], cwd=source.context)

    return inner

