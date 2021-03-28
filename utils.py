from abc import ABC
import re
from html.parser import HTMLParser
import logging
import config
import json
import functools
from urllib.request import urlopen

api_logger = logging.getLogger(config.LOGGER_NAME)


def handle_exception(logger, reraise=False):
	def decorator(func):
		@functools.wraps(func)
		def wrapper(*args, **kwargs):
			try:
				return func(*args, **kwargs)
			except Exception as e:
				logger.exception(e)
				if reraise:
					raise e

		return wrapper

	return decorator


def error_json(message):
	api_logger.error(message)
	return json.dumps({'Error': message})


@handle_exception(api_logger)
def get_rate():
	with urlopen(config.CURRENCY_RATE_URL, timeout=10) as response:
		response_content = response.read().decode('utf-8')
		parser = MyHTMLParser()
		parser.feed(response_content)
		return parser.get_rate()


@handle_exception(api_logger)
def calculate_usd(amount, rate):
	return str(float(amount) * rate)


class MyHTMLParser(HTMLParser, ABC):
	def __init__(self, *arg, **kwargs):
		super().__init__(*arg, **kwargs)
		self.caught_flag = False
		self.rates = []

	def get_rate(self):
		return self.rates[0]

	def handle_starttag(self, tag, attrs):
		if tag == 'div':
			for attr in attrs:
				if attr[0] == config.CSS_SELECTOR[0] and attr[1] == config.CSS_SELECTOR[1]:
					self.caught_flag = True

	@handle_exception(api_logger)
	def handle_data(self, data):
		if self.caught_flag:
			these_regex = r'\d*,\d*'
			pattern = re.compile(these_regex)
			rate = re.findall(pattern, data)
			self.rates.append(float(rate[0].replace(',', '.')))
		self.caught_flag = False
