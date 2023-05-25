import boto3
import pymysql
import json


def get_secret(secret_name, region_name):
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    get_secret_value_response = client.get_secret_value(
        SecretId=secret_name
    )

    if 'SecretString' in get_secret_value_response:
        secret = get_secret_value_response['SecretString']
    else:
        secret = base64.b64decode(get_secret_value_response['SecretBinary'])

    return json.loads(secret)


# test connection variables
test_db = {
    "host": "localhost",
    "username": "root",
    "password": "",
    "port": 8888,
    "db": "accounts_payable_local",
}


def connect():
    secrets = get_secret("aws_rds_secret", "eu-west-2")
    host = secrets['host']
    username = secrets['username']
    password = secrets['password']
    port = 3306
    dbname = 'accounts_payable_service_test'
    # test credentials
    # host = test_db['host']
    # username = test_db['username']
    # port = test_db['port']
    # password = test_db['password']
    # dbname = test_db['db']
    conn = pymysql.connect(host=host, port=port, user=username, password=password, db=dbname, connect_timeout=5)
    return conn
