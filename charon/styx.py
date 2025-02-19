from argparse import ArgumentError
import os
from .shared import load_config, get_task
import logging
from . import restic

_logger = logging.getLogger(__name__)

def parse_args(args):
    config = load_config(args.file)

    name = args.job
    jobs = config['jobs']
    if name not in jobs:
        print(f'no such job configured: {name}')
        print(f'available jobs:')
        for job_name in jobs.keys():
            print(f'    {job_name}')
        exit(1)

    job = jobs[name]

    return name, job

def apply(args):
    name, job = parse_args(args)

    _logger.info(f'[{name}] applying job')
    task = get_task(name, job)
    task()

def revert(args):
    name, job = parse_args(args)
    output_dir = os.path.abspath(args.output_dir)
    if os.path.isfile(output_dir):
        raise ValueError(f'[{name}] output_dir is a file: {output_dir}')
    if os.path.isdir(output_dir) and os.listdir(output_dir):
        raise ValueError(f'[{name}] directory exists and is not empty: {output_dir}')

    _logger.info(f'reverting job: {name} into {output_dir}')

    repo = restic.get_repository(name, job['repository'])
    repo.restore(output_dir)

