import logging
import os

import boto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError


LOG = logging.getLogger(__name__)


def assume_role(role_arn: str, profile_name: str, region: str):
    sts_client = boto3.client('sts')
    print(f'Going to assume role {role_arn}')

    session_token = sts_client.get_session_token()
    print(f"Credentials: {session_token['Credentials']}")
    print(f"AccessKeyId: {session_token['Credentials']['AccessKeyId']}")
    print(f"SecretAccessKey: {session_token['Credentials']['SecretAccessKey']}")
    print(f"SessionToken: {session_token['Credentials']['SessionToken']}")
    print(f"Expiration: {session_token['Credentials']['Expiration']}")

    try:
        response = sts_client.assume_role(RoleArn=role_arn, RoleSessionName=f'mgcp-cicd-session')
        print(response)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name.split('\\')[-1]

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


if __name__ == "__main__":
    load_dotenv()
    print("Prepare to upload package to s3")

    access_key = os.environ["AWS_ACCESS_KEY_ID"]
    secret_access_key = os.environ["AWS_SECRET_ACCESS_KEY"]
    AWS_SESSION_TOKEN = os.environ["AWS_SESSION_TOKEN"]
    AWS_SECURITY_TOKEN = os.environ["AWS_SECURITY_TOKEN"] 

    print("Get secret complete!")
    package = os.path.join(os.getcwd(), 'upload_sample.txt')
    print(f"uploading {package} to s3")

    upload_file(r"upload_sample.txt", 'mgcp-ops-cloudtrail-bucket-us-east-1')
    print("upload complete")