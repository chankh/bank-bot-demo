import bank
import boto3
import logging
import os
import requests
import shutil
import stat
import subprocess

page_id = os.getenv('PAGE_ID')
page_token = os.getenv('PAGE_TOKEN')

redirect_url = os.getenv('REDIRECT_URL')
bank_auth_url = os.getenv('BANK_AUTH_URL') + "?response_type=code&client_id=000000&scope=accounts_details_transactions%20customers_profiles%20payees%20personal_domestic_transfers%20internal_domestic_transfers%20external_domestic_transfers%20bill_payments&countryCode=HK&businessCode=GCB&locale=en_HK&redirect_uri=" + redirect_url + "&state="

bot_name = os.getenv('BOT_NAME')
bot_alias = os.getenv('BOT_ALIAS')
lex = boto3.client('lex-runtime', region_name='us-east-1')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

lambda_tmp_dir = '/tmp'  # Lambda fuction can use this directory.
local_source_audio = "{0}/downloaded.mp4".format(lambda_tmp_dir)
output_file = "{0}/output.wav".format(lambda_tmp_dir)


def is_lambda_runtime():
    return True if "LAMBDA_TASK_ROOT" in os.environ else False


if is_lambda_runtime():
    # ffmpeg is stored with this script.
    # When executing ffmpeg, execute permission is requierd.
    # But Lambda source directory do not have permission to change it.
    # So move ffmpeg binary to `/tmp` and add permission.
    ffmpeg_bin = "{0}/ffmpeg.linux64".format(lambda_tmp_dir)
    shutil.copyfile('/var/task/ffmpeg.linux64', ffmpeg_bin)
    os.environ['IMAGEIO_FFMPEG_EXE'] = ffmpeg_bin
    os.chmod(ffmpeg_bin, os.stat(ffmpeg_bin).st_mode | stat.S_IEXEC)


def lambda_handler(event, context):
    context = event['context']
    if context['http-method'] == 'GET':
        return verify_webhook(event['params']['querystring'], context)
    else:
        return process_event(event['body-json'], context)


def verify_webhook(query, context):
    if query['hub.mode'] == 'subscribe':
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
                    logger.warn("Webhook received unknown event: %s (id=%s, time=%s)" % (m, id, time))

    return True


def download_audio(audio_url):
    resp = requests.get(audio_url)
    download_to = local_source_audio
    if resp.status_code==200:
        with open(download_to, "wb") as fh:
            fh.write(resp.content)
    output = subprocess.check_output(["file", local_source_audio ])
    logger.debug("Audio file downloaded to {}".format(str(output, "utf-8")))


def transcode_audio():
    logger.debug('start transcode_audio()')
    resp = subprocess.check_output([ffmpeg_bin, '-i', local_source_audio, '-vn', '-acodec', 'pcm_s16le', '-ar', '16000', '-y', output_file])
    logger.debug(str(resp, "utf-8"))
    logger.debug(str(subprocess.check_output(["file", output_file]), "utf-8"))


def received_message(msg):
    sender_id = msg['sender']['id']
    recipient_id = msg['recipient']['id']
    timestamp = msg['timestamp']

    logger.debug("Received message for user %s and page %s at %d with message: %s" %
                 (sender_id, recipient_id, timestamp, msg))

    access_token = bank.check_auth(sender_id)
    if access_token is not None:
        if 'attachments' in msg['message']:
            msg_attachments = msg['message']['attachments']
            if msg_attachments[0]["type"]=="audio":
                audio_url = msg_attachments[0]["payload"]["url"]
                logger.debug("Received audio from %s" % audio_url)
                download_audio(audio_url)
                transcode_audio()
                ask_lex_content(sender_id, output_file)
        elif 'text' in msg['message']:
            msg_text = msg['message']['text']
            ask_lex(sender_id, msg_text)
        else:
            send_unknown(sender_id)
    else:
        ask_auth(sender_id)


def ask_lex_content(recipient_id, content):
    with open(content, 'rb') as file:
        resp = lex.post_content(
            botName=bot_name,
            botAlias=bot_alias,
            userId=recipient_id,
            contentType='audio/l16; rate=16000; channels=1',
            accept='audio/mpeg',
            inputStream=file
        )
        # print(resp)
        reply(recipient_id, resp['message'])


def ask_lex(recipient_id, message):
    try:
        resp = lex.post_text(
                botName=bot_name,
                botAlias=bot_alias,
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
                        "text": "Please authorize with bank to proceed",
                        "buttons": [{
                            "type": "web_url",
                            "url": bank_auth_url + user_id,
                            "title": "Authorize"
                            }]
                    }
                }
            }
        }
    logger.debug(message_data)

    call_message_api(message_data)
