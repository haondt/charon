import tempfile, sqlite3
import os

class SqliteSource:
    def __init__(self, path: str, filename: str):
        self._db_path = path
        self._filename = filename
        self._td: tempfile.TemporaryDirectory | None = None

    def __enter__(self):
        self._td = tempfile.TemporaryDirectory()

        backup_db_path = os.path.join(self._td.name, self._filename)
        with sqlite3.connect(self._db_path) as conn:
            with sqlite3.connect(backup_db_path) as backup_conn:
                conn.backup(backup_conn)

        return self

    def __exit__(self, *_):
        if self._td is not None:
            try:
                self._td.cleanup()
            finally:
                self._td = None
        return

    @property
    def context(self):
        if self._td is None:
            raise RuntimeError("Cannot provide context when temporary directory is unset.")
        return self._td.name

    @property
    def paths(self) -> list[str]:
        return ["."]

def create_sqlite_source(config):
    db_path = os.path.abspath(config['db_path'])
    db_file_name = os.path.basename(db_path)
    return SqliteSource(db_path, db_file_name)
