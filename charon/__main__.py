from .shared import load_config, get_task
from . import scheduling
import argparse
from . import styx
import logging

_logger = logging.getLogger(__name__)
LOG_TEMPLATE = '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s'
logging.basicConfig(format=LOG_TEMPLATE, level=logging.INFO)

DEFAULT_CONFIG_FILE = 'charon.yml'

def serve(args):
    config = load_config(args.file)

    scheduler_factory = scheduling.SchedulerFactory()
    for name, job in config['jobs'].items():
        schedule = job['schedule']
        task = get_task(name, job)
        timeout = schedule.get('timeout', None)
        if 'cron' in schedule:
            crontab = schedule['cron']
            scheduler_factory.add_cron(name, task, crontab, timeout=timeout)
        if 'after' in schedule:
            delay = schedule['after']
            scheduler_factory.add_once(name, task, delay, timeout=timeout)
        if 'every' in schedule:
            delay = schedule['every']
            scheduler_factory.add_every(name, task, delay, timeout=timeout)

    scheduler = scheduler_factory.build()

    scheduler.run()

def main():
    parser = argparse.ArgumentParser(prog='charon')
    parser.add_argument('-f', '--file', default=DEFAULT_CONFIG_FILE, help='configuration file')
    subparsers = parser.add_subparsers(dest='subcommand')

    revert_parser = subparsers.add_parser('revert')
    revert_parser.add_argument('job')
    revert_parser.add_argument('output_dir')

    apply_parser = subparsers.add_parser('apply')
    apply_parser.add_argument('job')

    args = parser.parse_args()
    if args.subcommand is None:
        _logger.info('running in service mode...')
        serve(args)
    elif args.subcommand == 'apply':
        styx.apply(args)
    elif args.subcommand == 'revert':
        styx.revert(args)

if __name__ == '__main__':
    main()
