import tempfile
import os
import requests
from requests.models import HTTPError
from .lib import _validate_and_decode_encryption_key, _tar, _untar, _encrypt, _decrypt, _get_file_extension



def task_factory(name, config):
    url = config['url']
    encryption_key = config.get('encrypt')
    encrypt = encryption_key is not None
    if encrypt:
        _validate_and_decode_encryption_key(encryption_key)

    headers = {}
    auth = config.get('auth')
    if auth is not None:
        if 'bearer' in auth:
            headers['Authorization'] = f'Bearer {auth["bearer"]}'
    method = config.get('method', 'get')
    extension = config.get('ext', 'txt')

    request = requests.Request(
        method = method.upper(),
        url = url,
        headers = headers
    ).prepare()

    def task(output_file: str):
        nonlocal encryption_key
        nonlocal encrypt
        nonlocal name
        nonlocal request
        nonlocal extension

        response = requests.Session().send(request, allow_redirects=False, timeout=30)
        if response.status_code != 200:
            raise HTTPError(f"received status code {response.status_code}")

        with tempfile.TemporaryDirectory() as td:
            initial_file_path = os.path.join(td, f'{name}.{extension}')
            with open(initial_file_path, 'w') as f:
                f.write(response.text)

            if encrypt:
                tar_file = os.path.join(td, f'{name}.tar.gz')
                _tar(initial_file_path, tar_file)
                _encrypt(encryption_key, tar_file, output_file)
            else:
                _tar(initial_file_path, output_file)

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
