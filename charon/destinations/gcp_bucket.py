from dataclasses import dataclass, field
from google.cloud import storage
import os


@dataclass
class GcpBucketConfigEntry:
    bucket: str

@dataclass
class GcpBucketConfig:
    entries: dict[str, GcpBucketConfigEntry] = field(default_factory=dict)

_config: GcpBucketConfig = GcpBucketConfig()

def configure(config):
    global _config
    _config = GcpBucketConfig()
    for k,v in config.items():
        _config.entries[k] = GcpBucketConfigEntry(v['bucket'])

def ensureCredentialsEnvVar():
    if os.getenv('GOOGLE_APPLICATION_CREDENTIALS') is None:
        raise EnvironmentError('missing environment variable GOOGLE_APPLICATION_CREDENTIALS')


def task_factory(config):
    output_name = config['name']
    config = _config.entries[config['config']] 

    def task(extension: str, input_file: str):
        nonlocal output_name
        nonlocal config

        ensureCredentialsEnvVar()

        target_path = f"{output_name}.{extension}"
        print(f'starting upload to gs://{config.bucket}/{target_path}')
        client = storage.Client()
        bucket = client.get_bucket(config.bucket)
        blob = bucket.blob(target_path)
        blob.upload_from_filename(input_file)
        print(f'finished upload to gs://{config.bucket}/{target_path}')
    return task

def revert(config, extension, output_file_path):
    ensureCredentialsEnvVar()
    output_name = config['name']
    config = _config.entries[config['config']] 
    target_path = f"{output_name}.{extension}"
    print(f'starting download from gs://{config.bucket}/{target_path}')
    client = storage.Client()
    bucket = client.get_bucket(config.bucket)
    blob = bucket.blob(target_path)
    blob.download_to_filename(output_file_path)
    print(f'finished download from to gs://{config.bucket}/{target_path}')
