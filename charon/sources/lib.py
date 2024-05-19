import os, tarfile, tempfile
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode

def _get_file_extension(config):
    if 'encrypt' in config:
        return 'enc'
    return 'tar.gz'

def _validate_and_decode_encryption_key(encryption_key) -> bytes:
    encryption_bytes = bytes.fromhex(encryption_key)
    if len(encryption_bytes) != 32:
        raise ValueError("encryption key must be 32 bytes long")
    return encryption_bytes

def _encrypt(encryption_key, input_file, output_file):
    encryption_bytes = _validate_and_decode_encryption_key(encryption_key)
    fernet = Fernet(urlsafe_b64encode(encryption_bytes))
    with open(input_file, 'rb') as f:
        original = f.read()
    encrypted  = fernet.encrypt(original)

    with open(output_file, 'wb') as f:
        f.write(encrypted)

def _decrypt(encryption_key, input_file, output_file):
    encryption_bytes = _validate_and_decode_encryption_key(encryption_key)
    fernet = Fernet(urlsafe_b64encode(encryption_bytes))
    with open(input_file, 'rb') as f:
        encrypted = f.read()
    original  = fernet.decrypt(encrypted)

    with open(output_file, 'wb') as f:
        f.write(original)

def _tar(input_path, output_file):
    input_path = os.path.abspath(input_path)
    if not os.path.exists(input_path):
        raise FileNotFoundError(input_path)
    current_dir = os.getcwd()
    try:
        working_dir = ''
        target = ''
        if os.path.isfile(input_path):
            working_dir = os.path.dirname(input_path)
            target = os.path.basename(input_path)
        else:
            working_dir = input_path
            target = '.'
        os.chdir(working_dir)
        with tarfile.open(output_file, "w:gz") as tar:
            tar.add(target)
    finally:
        os.chdir(current_dir)

def _untar(input_file, output_dir):
    if not os.path.exists(input_file):
        raise FileNotFoundError(input_file)
    with tarfile.open(input_file, "r:gz") as tar:
        tar.extractall(output_dir)

def _export_data(name, input_path, output_file, encryption_key: str | None=None):
    if encryption_key is not None:
        with tempfile.TemporaryDirectory() as td:
            tar_file = f'{name}.tar.gz'
            tar_file_path = os.path.join(td, tar_file)
            _tar(input_path, tar_file_path)
            _encrypt(encryption_key, tar_file_path, output_file)
    else:
        _tar(input_path, output_file)
