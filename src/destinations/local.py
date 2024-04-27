import os
import shutil

def task_factory(config):
    path = os.path.abspath(config['path'])
    output_name = config['name']
    overwrite = config.get('overwrite', False)

    def task(extension: str, input_file: str):
        nonlocal path
        nonlocal overwrite
        nonlocal output_name

        target_file = os.path.join(path, f"{output_name}.{extension}")

        if not overwrite:
            if os.path.exists(target_file):
                raise FileExistsError(f'file {target_file} already exists and overwrite is set to false')

        if os.path.isfile(path):
            raise FileExistsError(f'cannot create directory {path}: file exists')
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

        os.rename(input_file, target_file)

    return task

def revert(config, extension: str, output_file_path: str):
    path = os.path.abspath(config['path'])
    output_name = config['name']
    target_file = os.path.join(path, f"{output_name}.{extension}")

    if not os.path.isfile(target_file):
        raise FileNotFoundError(f'{target_file}: no such file')

    shutil.copy(target_file, output_file_path)
