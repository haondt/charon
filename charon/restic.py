import subprocess
import json
import os
import logging

_logger = logging.getLogger(__name__)

class Repository:
    def __init__(self, repo: str, password: str, binary: str = "restic", env_vars: dict[str, str]={}, max_snapshots: int|None = None, name: str='restic'):
        self._repo = repo
        self._password = password
        self._binary = binary
        self._env_vars = env_vars
        self._max_snapshots = max_snapshots
        self._name = name

    def _run(self, *args: str, capture_output: bool = False, cwd: str | None = None) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        env.update({
            "RESTIC_REPOSITORY": self._repo,
            "RESTIC_PASSWORD": self._password,
        })
        env.update(self._env_vars)

        _logger.info(f'[{self._name}] ' + ' '.join([self._binary, *args]))

        return subprocess.run([self._binary, *args], env=env, text=True, capture_output=capture_output, check=True, cwd=cwd)

    def __str__(self):
        return f'Restic Repository(repo={self._repo})'

    def init_repo(self) -> None:
        self._run("init")

    def backup(self, paths: list[str], cwd: str|None=None) -> None:
        self._run("backup", *paths, cwd=cwd)
        if (self._max_snapshots == 0 or self._max_snapshots == None):
            return
        self._run("forget", "--keep-last", str(self._max_snapshots))

    def exists(self):
        try:
            self._run("snapshots", "--json", capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            error_stderr = e.stderr if e.stderr else ""
            msg = error_stderr.lower()

            # local
            if "unable to open config file" in msg and "is there a repository at the following location?" in msg:
                return False

            # gcs
            if "parsing repository location failed: gs: invalid format: bucket name or path not found" in msg:
                return False

            raise ValueError("Unknown error reason: " + error_stderr) from e

    def snapshots(self) -> list[dict]:
        result = self._run("snapshots", "--json", capture_output=True)
        return json.loads(result.stdout)

    def restore(self, target: str, snapshot_id: str="latest") -> None:
        self._run("restore", snapshot_id, "--target", target)

    def forget(self, snapshot_id: str) -> None:
        self._run("forget", snapshot_id)

    def prune(self) -> None:
        self._run("prune")

def get_repository(name, config) -> Repository:
    backend_type = config['backend']['type']
    if backend_type == "local":
        return get_local_repository(name, config)
    if backend_type == "gcs_bucket":
        return get_gcs_repository(name, config)
    if backend_type == "rclone":
        return get_rclone_repository(name, config)
    raise KeyError(f'unknown backend type: {backend_type}')

def get_common_kwargs(name, config):
    kwargs = { 
        'password': config['password'],
        'name': name
    }
    if 'max_snapshots' in config:
        kwargs['max_snapshots'] = config['max_snapshots']
    return kwargs

# file based repository
def get_local_repository(name, config) -> Repository:
    path = os.path.abspath(config['backend']['path'])

    kwargs = get_common_kwargs(name, config)
    kwargs['repo'] = f"local:{path}"
    return Repository(**kwargs)

# Google Cloud Storage (GCS) repository
def get_gcs_repository(name, config) -> Repository:
    path = os.path.normpath(config['backend']['path']).lstrip('/')
    credentials = os.path.abspath(config['backend']['credentials'])
    bucket = config['backend']['bucket']
    repo = f"gs:{bucket}:{path}"

    kwargs = get_common_kwargs(name, config)
    kwargs['repo'] = repo
    kwargs['env_vars'] = {
        'GOOGLE_APPLICATION_CREDENTIALS': credentials
    }
    return Repository(**kwargs)

# rclone repository
def get_rclone_repository(name, config) -> Repository:
    path = os.path.normpath(config['backend']['path'])
    repo = f"rclone:{name}:{path}"

    rclone_config = config['backend']['rclone_config']
    rclone_config_name = name.upper()
    env_vars = { }
    for k, v in rclone_config.items():
        env_vars[f'RCLONE_CONFIG_{rclone_config_name}_{k.upper()}'] = str(v)

    kwargs = get_common_kwargs(name, config)
    kwargs['repo'] = repo
    kwargs['env_vars'] = env_vars
    return Repository(**kwargs)


