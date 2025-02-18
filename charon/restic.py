import subprocess
import json
import os

class Repository:
    def __init__(self, repo: str, password: str, binary: str = "restic"):
        self._repo = repo
        self._password = password
        self._binary = binary

    def _run(self, *args: str, capture_output: bool = False, cwd: str | None = None) -> subprocess.CompletedProcess:
        env = {
            "RESTIC_REPOSITORY": self._repo,
            "RESTIC_PASSWORD": self._password
        }
        return subprocess.run([self._binary, *args], env=env, text=True, capture_output=capture_output, check=True, cwd=cwd)

    def init_repo(self) -> None:
        self._run("init")

    def backup(self, paths: list[str], cwd: str|None=None) -> None:
        self._run("backup", *paths, cwd=cwd)

    def snapshots(self) -> list[dict]:
        result = self._run("snapshots", "--json", capture_output=True)
        return json.loads(result.stdout)

    def restore(self, target: str, snapshot_id: str="latest") -> None:
        self._run("restore", snapshot_id, "--target", target)

    def forget(self, snapshot_id: str) -> None:
        self._run("forget", snapshot_id)

    def prune(self) -> None:
        self._run("prune")

# file based repository
def get_local_repository(config) -> Repository:
    path = os.path.abspath(config['path'])
    return Repository(repo=f"file:{path}", password=config['password'])

# Google Cloud Storage (GCS) repository
def get_gcs_repository(config) -> Repository:
    repo = f"gs:{config['bucket']}/{config['path']}"
    return Repository(repo=repo, password=config['password'])

# SFTP repository (e.g., Hetzner Storage Box)
def get_sftp_repository(config) -> Repository:
    repo = f"sftp:{config['user']}@{config['host']}:{config['path']}"
    return Repository(repo=repo, password=config['password'])
