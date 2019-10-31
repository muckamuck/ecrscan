import logging
import datetime
import boto3
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
SEVERITIES = [
    'INFORMATIONAL',
    'LOW',
    'MEDIUM',
    'HIGH',
    'CRITICAL',
    'UNDEFINED'
]


def date_converter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


def init_boto3_clients(services, profile=None, region=None):
    '''
    Creates boto3 clients

    Args:
        profile - CLI profile to use
        region - where do you want the clients

    Returns:
        Good or Bad; True or False
    '''
    try:
        clients = {}
        session = None
        if profile and region:
            session = boto3.session.Session(profile_name=profile, region_name=region)
        elif profile:
            session = boto3.session.Session(profile_name=profile)
        elif region:
            session = boto3.session.Session(region_name=region)
        else:
            session = boto3.session.Session()

        for svc in services:
            clients[svc] = session.client(svc)

        return clients
    except Exception as wtf:
        logger.error(wtf, exc_info=False)
        return dict()


def get_results(ecr_client, repository, tag):
    '''
    Get scan results
    '''
    next_token = '__first__'
    try:
        while next_token:
            if next_token == '__first__':
                response = ecr_client.describe_image_scan_findings(
                    repositoryName=repository,
                    imageId={'imageTag':  tag}
                )
            else:
                response = ecr_client.describe_image_scan_findings(
                    repositoryName=repository,
                    imageId={'imageTag':  tag},
                    nextToken=next_token
                )

            next_token = response.get('nextToken', None)

        summary = response.get('imageScanFindings', {}).get('findingSeverityCounts', {})
        logger.debug(json.dumps(summary, indent=2, default=date_converter))
        for severity in SEVERITIES:
            logger.info('%s: %d', severity, summary.get(severity, 0))

        panic_count = summary.get('HIGH', 0) + summary.get('CRITICAL', 0)
        logger.info('%d reason(s) to panic', panic_count)

        return panic_count == 0
    except Exception as wtf:
        logger.error(wtf, exc_info=False)

    return False
