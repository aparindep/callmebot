import os
import boto3
import ast
from botocore.exceptions import ClientError
from dotenv import find_dotenv, load_dotenv, set_key

# get secrets from AWS Secrets Manager

def get_secret(secret_name):
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    secret = get_secret_value_response['SecretString']
    return ast.literal_eval(secret)

# load dotenv file

dotenv_file = find_dotenv('.env')
load_dotenv(dotenv_file)

s = get_secret("callmebot/psql")
set_key(
    dotenv_file,
    "DATABASE_URL",
    f"postgresql://{s['username']}:{s['password']}@{s['host']}:{s['port']}/{s['dbname']}"
)
set_key(
    dotenv_file,
    "TEST_DATABASE_URL",
    f"postgresql://{s['username']}:{s['password']}@{s['host']}:{s['port']}/{s['dbname'].replace('dev', 'test')}"
)
set_key(dotenv_file, "POSTGRES_USER", s['username'])
set_key(dotenv_file, "POSTGRES_PASSWORD", s['password'])

s = get_secret("callmebot/secret_key")
set_key(dotenv_file, "SECRET_KEY", s['secret_key'])
