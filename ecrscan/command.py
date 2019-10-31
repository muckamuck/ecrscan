'''
The command line interface to ECRScan.

Major help from: https://www.youtube.com/watch?v=kNke39OZ2k0
'''
import sys
import logging
import click
from ecrscan.utility import init_boto3_clients
from ecrscan.utility import get_results

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s (%(module)s) %(message)s',
    datefmt='%Y/%m/%d-%H:%M:%S'
)

SERVICES = ['ecr']
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@click.group()
@click.version_option(version='0.0.1')
def cli():
    '''
    A utility for working with ECR image scan results
    '''
    pass


@cli.command()
@click.option('--repository', '-r', help='ECR repository of interest', required=True)
@click.option('--tag', '-t', help='ECR repository tag of interest', required=True)
@click.option('--profile', help='AWS credential config')
@click.option('--region', help='AWS region')
def report(repository, tag, profile, region):
    '''
    The main reason we have arrived here. This is the entry-point for the
    utility report scan results.
    '''
    try:
        services = init_boto3_clients(SERVICES, profile, region)
        ecr_client = services.get('ecr')

        if ecr_client is None:
            logger.error('could not get an ECR client')
            sys.exit(1)

        if get_results(ecr_client, repository, tag):
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as wartburg_track_and_field:
        logger.error(wartburg_track_and_field, exc_info=False)

    sys.exit(2)
