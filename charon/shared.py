import tempfile
import os
import yaml
from . import sources
from . import destinations
from .sources import get_file_extension


def load_config(config_file):
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)

def configure_utils(config):
    destinations.gcp_bucket.configure(config.get('gcp_buckets', {}))

def source_factory(source_type):
    if (source_type == 'local'):
        return  sources.local
    if (source_type == 'http'):
        return  sources.http
    if (source_type == 'sqlite'):
        return  sources.sqlite
    raise KeyError(f'unknown source type: {source_type}')

def destination_factory(destination_type):
    if (destination_type == 'local'):
        return destinations.local
    if (destination_type == 'gcp_bucket'):
        return destinations.gcp_bucket
    raise KeyError(f'unknown destination type: {destination_type}')

def get_source_task_factory(source):
    source_type = source['type']
    return source_factory(source_type).task_factory

def get_destination_task_factory(destination):
    destination_type = destination['type']
    return destination_factory(destination_type).task_factory

def get_source_revert(source):
    source_type = source['type']
    return source_factory(source_type).revert

def get_destination_revert(destination):
    destination_type = destination['type']
    return destination_factory(destination_type).revert

def get_task(name, config):
    source = config['source']
    destination = config['destination']
    source_task, extension = get_source_task_factory(source)(name, source)
    destination_task = get_destination_task_factory(destination)(destination)

    def inner():
        nonlocal source_task
        nonlocal destination_task
        nonlocal extension
        with tempfile.TemporaryDirectory() as td:
            file_path = os.path.join(td, 'tmp')
            source_task(file_path)
            destination_task(extension, file_path)
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

