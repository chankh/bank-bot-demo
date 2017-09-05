import boto3
import logging
import os
import requests
import time
import uuid
from requests.auth import HTTPBasicAuth

try:
    import http.client as http_client
except ImportError:
    import httplib as http_client
http_client.HTTPConnection.debuglevel = 1

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

region = os.getenv('REGION')
dynamodb = boto3.resource('dynamodb', region_name=region)
table = dynamodb.Table('bank-bot-demo')

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')

redirect_uri = os.getenv('REDIRECT_URI')
bank_base_uri = os.getenv('BANK_BASE_URI')


def lambda_handler(event, context):
    params = event['params']['querystring']
    user_id = params['state']
    code = params['code']

    data = {"code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri}
    auth = HTTPBasicAuth(client_id, client_secret)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post(
            bank_base_uri + "/token",
            data=data,
            auth=auth,
            headers=headers)
    print(r)

    if r.status_code == 200:
        # success!
        resp = r.json()
        expire = resp['expires_in']
        resp['ttl'] = int(time.time() + expire)
        resp['user_id'] = user_id
        resp['name'] = retrieve_customer_name(resp['access_token'])
        table.put_item(Item=resp)
    else:
        print("Error retrieving access token from bank. %s" % r.text)

    return 'Authentication success! You may close this window now.'


def retrieve_customer_name(access_token):
    headers = {
        'Authorization': 'Bearer %s' % access_token,
        'uuid': str(uuid.uuid4()),
        'Accept': 'application/json',
        'client_id': client_id
    }
    r = requests.get(bank_base_uri + '/profiles',
                     headers=headers)

    if r.status_code != 200:
        return None

    info = r.json()
    name = info['name']
    name['prefix'] = info['prefix']
    return name
