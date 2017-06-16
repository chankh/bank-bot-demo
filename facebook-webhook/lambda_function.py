import boto3
import citi
import logging
import requests

page_id = "833374250162294"
page_token = "EAAGbZB0OBi7EBAOXOU0jZBoGfpem22Pm4RTL8CxSVSYevXCf9P0ZBgmLs0uLbcN2mGIiYqakOXN74Vrx51oTXwM7o9mTwSVJ08NZCk9RJpnae84Bac1TxoTjBLOvn6Nxsw9AMPpKvx9gXxgIZAukbpDxZCsryG8dav8cNmwstZBmQZDZD"

citi_auth_url = "https://sandbox.apihub.citi.com/gcb/api/authCode/oauth2/authorize?response_type=code&client_id=d738097c-6eea-4e5b-a1f2-35d816a65f07&scope=accounts_details_transactions%20customers_profiles%20payees%20personal_domestic_transfers%20internal_domestic_transfers%20external_domestic_transfers%20bill_payments&countryCode=HK&businessCode=GCB&locale=en_HK&redirect_uri=https://npkpenmw49.execute-api.us-east-1.amazonaws.com/v1/redirect&state="

lex = boto3.client('lex-runtime')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def lambda_handler(event, context):
    context = event['context']
    if context['http-method'] == 'GET':
        return verify_webhook(event['params']['querystring'], context)
    else:
        return process_event(event['body-json'], context)


def verify_webhook(query, context):
    if query['hub.mode'] == 'subscribe' and query['hub.verify_token'] == 'citi-demo-facebook':
        logger.info("Facebook webhook integration verified.")
        return int(query['hub.challenge'])


def process_event(event, context):
    if event['object'] == 'page':
        for e in event['entry']:
            id = e['id']
            time = e['time']

            for m in e['messaging']:
                if m['message'] is not None:
                    received_message(m)
                else:
                    logging.warn("Webhook received unknown event: %s (id=%s, time=%s)" % (m, id, time))

    return True


def received_message(msg):
    sender_id = msg['sender']['id']
    recipient_id = msg['recipient']['id']
    timestamp = msg['timestamp']
    msg_text = msg['message']['text']

    logger.debug("Received message for user %s and page %s at %d with message: %s" %
                 (sender_id, recipient_id, timestamp, msg_text))

    access_token = citi.check_auth(sender_id)
    if access_token is not None:
        if msg_text is not None:
            ask_lex(sender_id, msg_text)
        else:
            send_unknown(sender_id)
    else:
        ask_auth(sender_id)


def ask_lex(recipient_id, message):
    try:
        resp = lex.post_text(
                botName='CitiDemo',
                botAlias='Demo',
                userId=recipient_id,
                sessionAttributes={},
                inputText=message)
    except Exception as e:
        logger.error("Error received from Lex: {}".format(e))

    reply(recipient_id, resp['message'])


def send_unknown(recipient_id):
    reply(recipient_id, "Sorry I don't understand your message.")


def reply(recipient_id, message):
    message_data = {"recipient": {"id": recipient_id},
                    "message": {"text": message}}

    call_message_api(message_data)


def call_message_api(message_data):
    r = requests.post('https://graph.facebook.com/v2.6/me/messages',
                      params={"access_token": page_token},
                      json=message_data)

    if r.status_code != 200:
        logger.error("Unable to send message to facebook. %s" % r.json())


def ask_auth(user_id):
    message_data = {
            "recipient": {
                "id": user_id
            },
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "button",
                        "text": "Please authorize with Citibank to proceed",
                        "buttons": [{
                            "type": "web_url",
                            "url": citi_auth_url + user_id,
                            "title": "Authorize"
                            }]
                    }
                }
            }
        }

    call_message_api(message_data)
