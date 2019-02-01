from google.cloud import storage
from googleapiclient import discovery
from tempfile import TemporaryFile
from gmail import send_email
import logging


def remove_world_readable_buckets(event, context):
    """logs world-readable buckets with AllUsers or AllAuthenticatedUsers permissions"""
    alert = False
    world_bucket_total = []

    # open tempfile
    findings = TemporaryFile()
    opener = 'Hello, \n\nBelow are Google Cloud Storage World-Readable Permission Issues:\n\n'
    findings.write(bytes(opener, 'UTF-8'))

    logging.info('-----Checking for world-readable bucket permissions-----')
    for project_name in get_projects():
        storage_client = storage.Client(project=project_name)
        buckets = storage_client.list_buckets()

        try:
            for bucket in buckets:
                policy = bucket.get_iam_policy()
                for role in policy:
                    members = policy[role]

                    for member in members:
                        if member == 'allUsers' or member == 'allAuthenticatedUsers':
                            alert = True
                            if bucket.name not in world_bucket_total:
                                world_bucket_total.append(bucket.name)
                            logging.warning('"{0}" permissions were removed from Bucket "{1}" in project "{2}"'.
                                            format(member, bucket.name, project_name))
                            data = '"{0}" permissions were removed from Bucket "{1}" in project "{2}"' \
                                   '\n'.format(member, bucket.name, project_name)
                            findings.write(bytes(data, 'UTF-8'))

                            policy = bucket.get_iam_policy()
                            policy[role].discard(member)
                            bucket.set_iam_policy(policy)

        except Exception as err:
            logging.error(err)

    if alert is False:
        logging.info('No world-readable Bucket permissions found')

    else:
        # write tempfile to email body and delete
        findings.seek(0)
        email_body = findings.read().decode()
        send_email(email_body)
        print(email_body)
        findings.close()


def get_projects():
    project_list = []

    service = discovery.build('cloudresourcemanager', 'v1', cache_discovery=False)
    request = service.projects().list()
    while request is not None:
        response = request.execute()
        for project in response['projects']:
            if project['lifecycleState'] == 'ACTIVE':
                project_list.append(project['projectId'])

        request = service.projects().list_next(previous_request=request, previous_response=response)

    return project_list

if __name__ == '__main__':
    remove_world_readable_buckets(None, None)
