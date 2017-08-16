import boto3
import os
import requests

page_id = os.getenv('PAGE_ID')
page_token = os.getenv('PAGE_TOKEN')

region = os.getenv('REGION')
dynamodb = boto3.resource('dynamodb', region_name=region)
table = dynamodb.Table('bank-bot-demo')


def lambda_handler(event, context):
    # print("Received event: " + json.dumps(event, indent=2))
    for record in event['Records']:
        print(record['eventID'])
        print(record['eventName'])
        # print("DynamoDB Record: " + json.dumps(record['dynamodb'], indent=2))
        if record['eventName'] == 'INSERT':
            user_id = str(record['dynamodb']['Keys']['user_id']['S'])
            item = table.get_item(Key={'user_id': user_id})
            name = item['Item']['name']
            msg = "Hello %s, how are you? You can ask to show your account summary or make a transfer" % name['firstName']
            welcome(user_id, msg)

    return 'Successfully processed {} records.'.format(len(event['Records']))


def welcome(recipient_id, message):
    message_data = {"recipient": {"id": recipient_id},
                    "message": {"text": message}}

    call_message_api(message_data)


def call_message_api(message_data):
    r = requests.post('https://graph.facebook.com/v2.6/me/messages',
                      params={"access_token": page_token},
                      json=message_data)

    if r.status_code != 200:
        print("Unable to send message to facebook. %s" % r.json())
