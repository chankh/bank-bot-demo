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
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('citi-demo')

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')


def lambda_handler(event, context):
    params = event['params']['querystring']
    user_id = params['state']
    code = params['code']

    data = {"code": code,
            "grant_type": "authorization_code",
            "redirect_uri": "https://npkpenmw49.execute-api.us-east-1.amazonaws.com/v1/redirect"}
    auth = HTTPBasicAuth(client_id, client_secret)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post(
            'https://sandbox.apihub.citi.com/gcb/api/authCode/oauth2/token/hk/gcb',
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
        print("Error retrieving access token from Citibank. %s" % r.text)

    return 'Authentication success! You may close this window now.'


def retrieve_customer_name(access_token):
    headers = {
        'Authorization': 'Bearer %s' % access_token,
        'uuid': str(uuid.uuid4()),
        'Accept': 'application/json',
        'client_id': client_id
    }
    r = requests.get('https://sandbox.apihub.citi.com/gcb/api/v1/customers/profiles/basic',
                     headers=headers)

    if r.status_code != 200:
        return None

    info = r.json()['customerParticulars']
    name = info['names'][0]
    name['prefix'] = info['prefix']
    return name
