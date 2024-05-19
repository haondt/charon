import tempfile, sqlite3
import os
from .lib import _validate_and_decode_encryption_key, _untar, _decrypt, _get_file_extension, _export_data

def task_factory(name, config):
    db_path = os.path.abspath(config['db_path'])
    db_file_name = os.path.basename(db_path)
    encryption_key = config.get('encrypt')
    if encryption_key is not None:
        _validate_and_decode_encryption_key(encryption_key)

    def task(output_file: str):
        nonlocal db_path
        nonlocal encryption_key
        nonlocal name

        with tempfile.TemporaryDirectory() as td:
            backup_db_path = os.path.join(td, db_file_name)
            with sqlite3.connect(db_path) as conn:
                with sqlite3.connect(backup_db_path) as backup_conn:
                    conn.backup(backup_conn)

            _export_data(name, backup_db_path, output_file, encryption_key)

    return task, _get_file_extension(config)

def revert(config, input_file, output_dir='.'):
    encryption_key = config.get('encrypt')
    encrypt = encryption_key is not None
    if encrypt:
        _validate_and_decode_encryption_key(encryption_key)
        with tempfile.TemporaryDirectory() as td:
            tar_file = os.path.join(td, 'tmp.tar.gz')
            _decrypt(encryption_key, input_file, tar_file)
            _untar(tar_file, output_dir)
    else:
       _untar(input_file, output_dir)
