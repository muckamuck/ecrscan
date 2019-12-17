import sys
import logging
import datetime
import time
import boto3
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

IN_PROGRESS = 'IN_PROGRESS'
COMPLETE = 'COMPLETE'
FAILED = 'FAILED'

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


def scan_image(ecr_client, repository, tag):
    try:
        response = ecr_client.start_image_scan(
            repositoryName=repository,
            imageId={'imageTag':  tag}
        )
        logger.info('start_image_scan response: %s', json.dumps(response, indent=2, default=date_converter))
        return get_results(ecr_client, repository, tag)
    except Exception as wtf:
        logger.error(wtf, exc_info=False)

    return False


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
                current_status = response.get('imageScanStatus').get('status', 'FAILED')
                logger.info('current scan status is %s', current_status)
                if current_status == FAILED:
                    logger.error('exiting')
                    sys.exit(1)
                elif current_status == IN_PROGRESS:
                    time.sleep(15)
                    continue
                elif current_status == COMPLETE:
                    logger.debug('move along')
                else:
                    logger.error('strange scan status, running away')
                    sys.exit(1)
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
