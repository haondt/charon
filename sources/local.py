import tempfile
import os
from .lib import _validate_and_decode_encryption_key, _tar, _untar, _encrypt, _decrypt, _get_file_extension

def task_factory(name, config):
    path = os.path.abspath(config['path'])
    encryption_key = config.get('encrypt')
    encrypt = encryption_key is not None
    if encrypt:
        _validate_and_decode_encryption_key(encryption_key)

    def task(output_file: str):
        nonlocal path
        nonlocal encryption_key
        nonlocal encrypt
        nonlocal name

        if encrypt:
            with tempfile.TemporaryDirectory() as td:
                tar_file = f'{name}.tar.gz'
                tar_file_path = os.path.join(td, tar_file)
                _tar(path, tar_file_path)
                _encrypt(encryption_key, tar_file_path, output_file)
        else:
            _tar(path, output_file)

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
