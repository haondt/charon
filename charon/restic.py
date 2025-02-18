import subprocess
import json
import os
import logging

_logger = logging.getLogger(__name__)

class Repository:
    def __init__(self, repo: str, password: str, binary: str = "restic", env_vars: dict[str, str]={}):
        self._repo = repo
        self._password = password
        self._binary = binary
        self._env_vars = env_vars

    def _run(self, *args: str, capture_output: bool = False, cwd: str | None = None) -> subprocess.CompletedProcess:
        env = {
            "RESTIC_REPOSITORY": self._repo,
            "RESTIC_PASSWORD": self._password
        }
        for k, v in self._env_vars.items():
            env[k] = v

        _logger.info(f'RESTIC_REPOSITORY={self._repo} ' + ' '.join([self._binary, *args]))
        return subprocess.run([self._binary, *args], env=env, text=True, capture_output=capture_output, check=True, cwd=cwd)

    def __str__(self):
        return f'Restic Repository(repo={self._repo})'

    def init_repo(self) -> None:
        self._run("init")

    def backup(self, paths: list[str], cwd: str|None=None) -> None:
        self._run("backup", *paths, cwd=cwd)

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

def get_repository(config) -> Repository:
    backend_type = config['backend']['type']
    if backend_type == "local":
        return get_local_repository(config)
    if backend_type == "gcs_bucket":
        return get_gcs_repository(config)
    if backend_type == "sftp":
        return get_sftp_repository(config)
    raise KeyError(f'unknown backend type: {backend_type}')


# file based repository
def get_local_repository(config) -> Repository:
    path = os.path.abspath(config['backend']['path'])
    return Repository(repo=f"local:{path}", password=config['password'])

# Google Cloud Storage (GCS) repository
def get_gcs_repository(config) -> Repository:
    path = os.path.normpath(config['backend']['path']).lstrip('/')
    credentials = os.path.abspath(config['backend']['credentials'])
    bucket = config['backend']['bucket']
    repo = f"gs:{bucket}:{path}"
    return Repository(repo=repo, password=config['password'], env_vars={'GOOGLE_APPLICATION_CREDENTIALS': credentials})

# SFTP repository (e.g., Hetzner Storage Box)
def get_sftp_repository(config) -> Repository:
    path = os.path.normpath(config['backend']['path']).lstrip('/')
    user = config['backend']['user']
    host = config['backend']['host']
    repo = f"sftp:{user}@{host}:{path}"
    return Repository(repo=repo, password=config['password'])
