import os
from .shared import load_config, configure_utils, get_task, revert

def configure_parser(parser):
    sub_parsers = parser.add_subparsers(dest='styx_command', required=True)
    revert_parser = sub_parsers.add_parser('revert')
    revert_parser.add_argument('job')
    revert_parser.add_argument('output_dir')
    apply_parser = sub_parsers.add_parser('apply')
    apply_parser.add_argument('job')

def execute(args):
    config = load_config(args.file)
    configure_utils(config)

    name = args.job
    jobs = config['jobs']
    if name not in jobs:
        print(f'no such job configured: {name}')
        print(f'available jobs:')
        for job_name in jobs.keys():
            print(f'    {job_name}')
        exit(1)

    job = jobs[name]

    if args.styx_command == 'apply':
        print(f'applying job: {name}')
        task = get_task(name, job)
        task()
    elif args.styx_command == 'revert':
        output_dir = os.path.abspath(args.output_dir)
        if os.path.isfile(output_dir):
            print(f'output_dir is a file: {output_dir}')
            exit(1)
        if not os.path.isdir(output_dir):
            print(f'directory does not exist: {output_dir}')
            exit(1)

        print(f'reverting job: {name} into {output_dir}')
        revert(job, output_dir)


