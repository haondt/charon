from .shared import load_config, configure_utils, get_task
from . import scheduling
import argparse
from . import styx

DEFAULT_CONFIG_FILE = 'charon.yml'

def serve(args):
    config = load_config(args.file)
    configure_utils(config)

    scheduler_factory = scheduling.SchedulerFactory()
    for name, job in config['jobs'].items():
        schedule = job['schedule']
        task = get_task(name, job)
        if 'cron' in schedule:
            crontab = schedule['cron']
            scheduler_factory.add_cron(name, task, crontab)
        if 'after' in schedule:
            delay = schedule['after']
            scheduler_factory.add_once(name, task, delay)
        if 'every' in schedule:
            delay = schedule['every']
            scheduler_factory.add_every(name, task, delay)

    scheduler = scheduler_factory.build()

    scheduler.run()

def main():
    parser = argparse.ArgumentParser(prog='charon')
    parser.add_argument('-f', '--file', default=DEFAULT_CONFIG_FILE, help='configuration file')
    subparsers = parser.add_subparsers(dest='subcommand')

    styx_parser = subparsers.add_parser('styx')
    styx.configure_parser(styx_parser)

    args = parser.parse_args()
    if args.subcommand is None:
        print('running in service mode...')
        serve(args)
    elif args.subcommand == 'styx':
        styx.execute(args)

if __name__ == '__main__':
    main()
