import bank
import boto3
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

region = os.getenv('REGION')
dynamodb = boto3.resource('dynamodb', region_name=region)
table = dynamodb.Table('bank-bot-demo')


def transfer_money(user_token, event, attributes):
    intent = event['currentIntent']
    invocation = event['invocationSource']
    intent_name = intent['name']
    slots = intent['slots']
    # let's fetch some account info from bank
    accounts = bank.retrieve_dest_src_acct(user_token)

    if invocation == 'DialogCodeHook':
        validation_result = validate_transfer(slots, attributes, accounts)
        if not validation_result['isValid']:
            violated_slot = validation_result['violatedSlot']
            logger.debug('Slot {} is invalid: {}'.format(violated_slot, slots[violated_slot]))
            slots[violated_slot] = None

            elicit = elicit_slot(
                    attributes,
                    intent_name,
                    slots,
                    violated_slot,
                    validation_result['message']
            )
            logger.debug("Elicit response: {}".format(elicit))
            return elicit

        # Create a transfer request here
        if intent['confirmationStatus'] == 'None':

            """
            control_flow_id = bank.create_transfer(
                    user_token,
                    attributes['source_account_id'],
                    attributes['amount'],
                    attributes['destination_account_id'])

            if control_flow_id is None:
                return close(
                    attributes,
                    'Failed',
                    {
                        'contentType': 'PlainText',
                        'content': 'Cannot create a transfer request, please contact helpdesk.'
                    }
                )
            attributes['control_flow_id'] = control_flow_id
            """
            confirm_msg = "Are you sure to transfer %s $%s from %s to %s?" % (attributes['currency'], slots['amount'], attributes['source_name'], attributes['destination_name'])
            return confirm(
                attributes,
                {
                    'contentType': 'PlainText',
                    'content': confirm_msg
                },
                intent_name,
                slots
            )
        else:
            return delegate(attributes, slots)

    # t = bank.make_transfer(user_token, attributes['control_flow_id'])
    # Fulfillment, confirming the transfer
    ref_id = 'HBKFT738X6901667831'
    return close(
        attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Your transfer is completed. Here is the reference number %s' % ref_id
        }
    )


def validate_transfer(slots, attributes, accounts):
    # validate slots one by one
    dest = is_valid_destination(slots['destination'], accounts)
    if dest is None:
        destinations = ""
        for d in accounts['destinationSourceAcctCombinations']:
            destinations += '- %s\n' % d['productName']
        return build_validation_result(
                False,
                'destination',
                "Which account to transfer to?\n" + destinations
        )

    if attributes is None:
        attributes = []
    attributes['destination_account_id'] = dest['destinationAccountId']
    attributes['destination_name'] = dest['productName']
    dest_id = dest['destinationAccountId']

    source = is_valid_source(slots['source'], dest_id, accounts)
    if source is None:
        sources = ""
        source_accounts = get_possible_sources(dest_id, accounts)
        logger.debug("Possible source accounts: {}".format(source_accounts))

        for s in source_accounts:
            sources += '- %s (%s $%.2f)\n' % (s['productName'], s['sourceAccountCurrencyCode'], s['availableBalance'])
        return build_validation_result(
                False,
                'source',
                "From which account?\n" + sources
        )

    source_id = source['sourceAccountId']
    attributes['source_account_id'] = source_id
    attributes['source_name'] = source['productName']
    attributes['currency'] = source['sourceAccountCurrencyCode']

    if slots['amount'] is None:
        return build_validation_result(
                False,
                'amount',
                'Please enter the amount to transfer.'
        )

    amount = is_valid_amount(slots['amount'], source_id, accounts)
    if amount is None:
        return build_validation_result(
                False,
                'amount',
                "Sorry this amount is invalid, please re-enter."
        )
    attributes['amount'] = amount

    return {'isValid': True}


def show_accounts(user_token, intent, attributes):
    slots = intent['slots']
    logger.debug("retrieving accounts information, slots={}".format(slots))
    account_group = is_valid_account_group(slots['accountGroup'])

    if account_group is None:
        logger.debug("Unknown account group: {}".format(slots['accountGroup']))
        return elicit_slot(
                attributes, intent['name'], slots, 'accountGroup',
                {
                    'contentType': 'PlainText',
                    'content': 'Valid account types are:\n- Savings and Investments\n- Checking\n- Insurance'
                }
        )

    summary = bank.get_account_summary(user_token, account_group)
    if summary is None:
        resp = "You do not have any accounts of this type."
    else:
        resp = "Here are your accounts:\n"

    if 'SAVINGS_AND_INVESTMENTS' == account_group or 'CHECKING' == account_group:
        resp += prepare_accounts_response(summary)
    elif 'INSURANCE' == account_group:
        resp += prepare_insurance_response(summary)

    return close(
        attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': resp
        }
    )


def prepare_accounts_response(summary):
    i = 1
    r = ""
    for a in summary['accounts']:
        key = next(iter(a.keys()))
        s = a[key]
        r = r + "%d. %s (%s) - %s $%.2f\n" % (i, s['productName'], s['displayAccountNumber'], s['currencyCode'], s['currentBalance'])
        i = i + 1

    total = summary['totalCurrentBalance']
    r = r + "Total %d accounts, %s $%.2f" % (i, total['localCurrencyCode'], total['localCurrencyBalanceAmount'])
    return r


def prepare_insurance_response(summary):
    i = 1
    r = ""
    for p in summary['insurancePolicies']:
        r = r + "%d. %s (%s)\n" % (i, p['productName'], p['displayAccountNumber'])
        i = i + 1

    r = r + "Total %d insurance policies." % i

    return r

# -- Validation


def is_valid_destination(destination, accounts):
    for d in accounts['destinationSourceAcctCombinations']:
        if destination is not None and d['productName'].upper() == destination.upper():
            return d

    return None


def is_valid_source(source_account, destination_account_id, accounts):
    source_account_id = None
    for a in accounts['sourceAccounts']:
        if source_account is not None and a['productName'].upper() == source_account.upper():
            source_account_id = a['sourceAccountId']

    if source_account_id is None:
        return None

    d = get_destination_account(destination_account_id, accounts)
    if d is not None:
        for s in d['sourceAccountIds']:
            if s['sourceAccountId'] == source_account_id:
                return get_source_account(s['sourceAccountId'], accounts['sourceAccounts'])

    return None


def get_possible_sources(destination_account_id, accounts):
    d = get_destination_account(destination_account_id, accounts)
    logger.debug("getting source accounts from destination account {}".format(d))
    sources = []
    for i in d['sourceAccountIds']:
        s = get_source_account(i['sourceAccountId'], accounts['sourceAccounts'])
        if s is not None:
            sources.append(s)

    return sources


def get_source_account(source_account_id, accounts):
    logger.debug('getting source account {} from {}'.format(source_account_id, accounts))
    for s in accounts:
        if s['sourceAccountId'] == source_account_id:
            return s

    return None


def get_destination_account(destination_account_id, accounts):
    for d in accounts['destinationSourceAcctCombinations']:
        if d['destinationAccountId'] == destination_account_id:
            return d

    return None


def is_valid_amount(amount, source_account_id, accounts):
    if amount is None:
        return False

    if amount[0] == '$':
        amount = amount[1:]

    amount = float(amount)
    for a in accounts['sourceAccounts']:
        if a['sourceAccountId'] == source_account_id:
            logger.debug("Comparing {} with {}".format(amount, a['availableBalance']))
            if amount <= a['availableBalance']:
                return amount


def is_valid_account_group(accountGroup):
    if accountGroup is None:
        return None

    group = accountGroup.lower()
    if group == 'saving' or  group == 'savings' or group == 'investment' or group == 'investments' or group == 'savings and investments':
        return 'SAVINGS_AND_INVESTMENTS'
    if group == 'checking' or group == 'cheque':
        return 'CHECKING'
    if group == 'insurance' or group == 'insurances':
        return 'INSURANCE'

    return None


# -- Helpers that build all of the responses


def build_validation_result(is_valid, violated_slot, message_content):
    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def confirm(session_attributes, message, intent_name, slots):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ConfirmIntent',
            'message': message,
            'intentName': intent_name,
            'slots': slots
        }
    }

    return response


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


# -- Helpers
def get_access_token(user_id):
    try:
        item = table.get_item(Key={'user_id': user_id})
        access_token = item['Item']['access_token']
        print("Retrieved token %s for user %s" % (access_token, user_id))
        return access_token
    except Exception as e:
        logger.error("Unable to retrieve access token for user " + user_id, e)
        return None


def dispatch(event):
    user_id = event['userId']
    intent = event['currentIntent']
    attributes = event['sessionAttributes']
    name = intent['name']
    logger.debug("dispatch userId={}, intentName={}".format(user_id, name))
    access_token = get_access_token(user_id)

    if access_token is None:
        return close(attributes, 'Failed', 'You are not authenticated.')

    if name == 'ShowAccounts':
        return show_accounts(access_token, intent, attributes)
    if name == 'MoneyMovement':
        return transfer_money(access_token, event, attributes)

    raise Exception('Intent with name ' + name + ' not supported')


def lambda_handler(event, context):
    logger.debug(event)
    bot_name = event['bot']['name']
    if bot_name == 'BankDemo':
        return dispatch(event)

    Exception('Invocation from unknown bot ' + bot_name)
