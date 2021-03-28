import json
from utils import get_rate, calculate_usd, error_json
import logging
import config

api_logger = logging.getLogger(config.LOGGER_NAME)


def index(header, **kwargs):
    amount = kwargs.get('amount', '')
    if not amount:
        header = 'HTTP/1.1 400 Amount parameter not found\n\n'
        return header, error_json('Amount parameter not found.')
    rate = get_rate()
    if not rate:
        header = 'HTTP/1.1 500 Bad currency rates service\n\n'
        return header, error_json('Bad currency rates service.')
    usd_amount = calculate_usd(amount, rate)
    if not usd_amount:
        header = 'HTTP/1.1 400 Amount should be float\n\n'
        return header, error_json('Amount should be float.')
    api_logger.debug('Amount: ' + amount + ' Rate: ' + str(rate) + ' Result: ' + usd_amount)
    return header, json.dumps({'Currency': 'USD', u'Amount': amount, 'Rate': str(rate), 'Result': usd_amount})


def return_405(**kwargs):
    return error_json('Method not allowed')


def return_404(**kwargs):
    return error_json('Page not found')
