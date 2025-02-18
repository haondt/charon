import tempfile
import os
import yaml
from . import sources
from . import restic


def load_config(config_file):
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)

def get_task(name, config):
    source = config['source']
    destination = config['destination']

    source_type = source['type']
    if source_type == "local":
        source_factory = lambda: sources.local.create_local_source(source)
    # elif source_type == "http":
    #     source_factory = sources.http.create_http_source(name, source)
    # elif source_type == "sqlite":
    #     TODO
    else:
        raise KeyError(f'unknown source type: {source_type}')

    destination_type = destination["type"]
    if destination_type == "local":
        repo = restic.get_local_repository(destination)
    elif destination_type == "gcs_bucket":
        repo = restic.get_gcs_repository(config)
    elif destination_type == "sftp":
        repo = restic.get_sftp_repository(config)
    else:
        raise KeyError(f'unknown destination type: {source_type}')

    def inner():
        nonlocal source_factory
        nonlocal repo
        with source_factory() as source:
            repo.backup([source.path], cwd=source.context)

    return inner

def revert(config, output_dir: str):
    source = config['source']
    destination = config['destination']
    source_revert = get_source_revert(source)
    destination_revert = get_destination_revert(destination)

    with tempfile.TemporaryDirectory() as td:
        file_path = os.path.join(td, 'tmp')
        extension = get_file_extension(source)
        destination_revert(destination, extension, file_path)
        source_revert(source, file_path, output_dir)

