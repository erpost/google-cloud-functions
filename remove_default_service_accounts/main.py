from googleapiclient import discovery
from tempfile import TemporaryFile
from gmail import send_email
import logging


def remove_default_service_accounts(event, context):
    """removes Default Service Accounts from Google Cloud Platform"""
    alert = False

    # open tempfile
    findings = TemporaryFile()
    opener = 'Hello, \n\nBelow are Google Cloud Platform Default Service Accounts that were removed:\n\n'
    findings.write(bytes(opener, 'UTF-8'))

    logging.info('-----Checking for Default User Accounts-----')
    for project in get_projects():
        project_name = 'projects/' + project
        try:
            service = discovery.build('iam', 'v1', cache_discovery=False)
            request = service.projects().serviceAccounts().list(name=project_name)
            response = request.execute()
            accounts = response['accounts']

            for account in accounts:
                serviceaccount = account['email']

                if 'gserviceaccount.com' in serviceaccount and 'iam' not in serviceaccount:
                    alert = True
                    service_account = project_name + '/serviceAccounts/' + serviceaccount
                    delete_request = service.projects().serviceAccounts().delete(name=service_account)
                    delete_request.execute()
                    logging.warning('Default Service Account "{0}" deleted from project "{1}"'.
                                    format(serviceaccount, project))
                    data = '{0} removed from {1}\n\n'.format(serviceaccount, project)
                    findings.write(bytes(data, 'UTF-8'))
        except KeyError:
            logging.info('No Service Accounts found in project "{0}"'.format(project))

        except Exception as err:
            logging.error(err)

    if alert is False:
        logging.info('No Default Service Accounts found')

    else:
        # write tempfile to email body and delete
        findings.seek(0)
        email_body = findings.read().decode()
        send_email(email_body)
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
    remove_default_service_accounts(None, None)
