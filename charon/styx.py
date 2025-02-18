import os
from .shared import load_config, get_task, revert

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

    print(f'applying job: {name}')
    task = get_task(name, job)
    task()

def revert(args):
    name, job = parse_args(args)
    output_dir = os.path.abspath(args.output_dir)
    if os.path.isfile(output_dir):
        print(f'output_dir is a file: {output_dir}')
        exit(1)
    if not os.path.isdir(output_dir):
        print(f'directory does not exist: {output_dir}')
        exit(1)

    print(f'reverting job: {name} into {output_dir}')
    revert(job, output_dir)
