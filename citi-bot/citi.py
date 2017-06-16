import logging
import requests
import time
import uuid
try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client


http_client.HTTPConnection.debuglevel = 1

client_id = "d738097c-6eea-4e5b-a1f2-35d816a65f07"
client_secret = "sX7jA5aF7hE7fC7oK1qX1aG1iH0kM8xN0mS2kN5mF0mF7lN0qT"

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


def get_account_summary(token, group):
    headers = generate_headers(token)
    r = requests.get("https://sandbox.apihub.citi.com/gcb/api/v1/accounts",
                     headers=headers)

    if r.status_code != 200:
        logger.error("Unable to get account summary, status={}, error={}".format(r.status_code, r.text))
        return None

    summary = r.json()
    logger.debug(summary)
    for a in summary['accountGroupSummary']:
        if a['accountGroup'] == group:
            return a


def retrieve_dest_src_acct(token):
    headers = generate_headers(token)
    r = requests.get(
            "https://sandbox.apihub.citi.com/gcb/api/v1/moneyMovement/personalDomesticTransfers/destinationAccounts/sourceAccounts",
            headers=headers)

    if r.status_code != 200:
        logger.error("Unable to get account summary, status={}, error={}".format(r.status_code, r.text))
        return None

    return r.json()


def create_transfer(token, source_account_id, amount, destination_account_id):
    request = {
        "sourceAccountId": source_account_id,
        "transactionAmount": amount,
        "transferCurrencyIndicator": "SOURCE_ACCOUNT_CURRENCY",
        "destinationAccountId": destination_account_id,
        "chargeBearer": "BENEFICIARY",
        "fxDealReferenceNumber": "FB%d" % int(time.time()),
        "remarks": "",
        "transferPurpose": "CASH_DISBURSEMENT"
    }

    headers = generate_headers(token)
    r = requests.post('https://sandbox.apihub.citi.com/gcp/api/v1/moneyMovement/personalDomesticTransfers/preprocess',
                      json=request,
                      headers=headers)

    if r.status_code != 200:
        logger.error("Unable to create transfer request, status={}, error={}".format(r.status_code, r.text))
        return None

    j = r.json()
    return j['controlFlowId']


def make_transfer(token, control_flow_id):
    request = {"controlFlowId": control_flow_id}
    headers = generate_headers(token)
    r = requests.post('https://sandbox.apihub.citi.com/gcb/api/v1/moneyMovement/personalDomesticTransfers',
                      json=request,
                      headers=headers)

    if r.status_code != 200:
        logger.error("Unable to create transfer request, status={}, error={}".format(r.status_code, r.text))
        return None

    return r.json()


def generate_headers(token):
    return {
        "Authorization": "Bearer %s" % token,
        "uuid": str(uuid.uuid4()),
        "client_id": client_id,
        "Accept": "application/json"
    }
