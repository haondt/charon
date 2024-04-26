from dataclasses import dataclass, field

@dataclass
class GcpBucketConfigEntry:
    credentials: str
    bucket: str

@dataclass
class GcpBucketConfig:
    entries: dict[str, GcpBucketConfigEntry] = field(default_factory=dict)

_config: GcpBucketConfig | None = None

def configure(config):
    _config = GcpBucketConfig()
    for k,v in config.items():
        _config.entries[k] = GcpBucketConfigEntry(v['credentials'], v['bucket'])

def task_factory(config):
    def task(extension: str, input_file: str):
        pass
    return task

def revert(config, extension, output_file_path):
    pass
