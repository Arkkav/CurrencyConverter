import json
from utils import get_rate, calculate_usd, error_json
import logging
import config
from typing import Optional, Any


api_logger = logging.getLogger(config.LOGGER_NAME)


def index(header: str, **kwargs: Any) -> tuple[str, str]:
    amount: str = kwargs.get('amount', '')
    if not amount:
        header = 'HTTP/1.1 400 Amount parameter not found\n\n'  # If no amount parameter then return 400
        return header, error_json('Amount parameter not found.')
    rate: Optional[float] = get_rate()
    if not rate:
        # If no such CSS selector at all for source and selector in config)
        header = 'HTTP/1.1 500 Bad currency rates service\n\n'
        return header, error_json('Bad currency rates service.')
    usd_amount: str = calculate_usd(amount, rate)
    if not usd_amount:
        header = 'HTTP/1.1 400 Amount should be float\n\n'  # If amount parameter has bed format then return 500
        return header, error_json('Amount should be float.')
    api_logger.debug('Amount: ' + amount + ' Rate: ' + str(rate) + ' Result: ' + usd_amount)
    return header, json.dumps({'Currency': 'USD', u'Amount': amount, 'Rate': str(rate), 'Result': usd_amount})


def return_405(**kwargs) -> str:
    return error_json('Method not allowed')


def return_404(**kwargs) -> str:
    return error_json('Page not found')
