import boto3
import requests

page_id = "833374250162294"
page_token = "EAAGbZB0OBi7EBAOXOU0jZBoGfpem22Pm4RTL8CxSVSYevXCf9P0ZBgmLs0uLbcN2mGIiYqakOXN74Vrx51oTXwM7o9mTwSVJ08NZCk9RJpnae84Bac1TxoTjBLOvn6Nxsw9AMPpKvx9gXxgIZAukbpDxZCsryG8dav8cNmwstZBmQZDZD"

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('citi-demo')


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
            welcome(user_id, "Hello %s, how may I help you?" % name['firstName'])

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
