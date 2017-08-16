import boto3
import logging
import os
import time

region = os.geten('REGION')
dynamodb = boto3.resource('dynamodb', region_name=region)
table = dynamodb.Table('bank-bot-demo')
log = logging.getLogger()
log.setLevel(logging.DEBUG)


def check_auth(user_id):
    key = {'user_id': user_id}
    try:
        record = table.get_item(Key=key)
        item = record['Item']
        if int(time.time()) > item['ttl']:
            log.info('Token {} expired.'.format(item))
            table.delete_item(Key=key)
            return None
        access_token = item['access_token']
        log.debug("Retrieved token %s for user %s" % (access_token, user_id))
        return access_token
    except Exception as e:
        log.error(e)
        return None


def save_auth(user_id):
    pass
