from abc import ABC
import re
from html.parser import HTMLParser
import logging
import config
import json
import functools
from urllib.request import urlopen
from typing import Optional, Any, Callable

api_logger: logging.Logger = logging.getLogger(config.LOGGER_NAME)


def handle_exception(logger: logging.Logger, reraise: bool = False) -> Callable[..., Any]:
	def decorator(func):
		@functools.wraps(func)
		def wrapper(*args: Any, **kwargs: Any):
			try:
				return func(*args, **kwargs)
			except Exception as e:
				logger.exception(e)
				if reraise:
					raise e

		return wrapper

	return decorator


def error_json(message: str) -> str:
	api_logger.error(message)
	return json.dumps({'Error': message})


@handle_exception(api_logger)
def get_page(url: str) -> tuple[int, str]:
	# Get HTML from address and port
	with urlopen(url, timeout=10) as response:
		return response.code, response.read().decode('utf-8')


def get_rate() -> Optional[float]:
	# Get rate from HTML
	code: int
	response_content: str
	code, response_content = get_page(config.CURRENCY_RATE_URL)
	parser: MyHTMLParser = MyHTMLParser(config.CSS_SELECTOR[0], config.CSS_SELECTOR[1], config.CSS_SELECTOR[2])
	parser.feed(response_content)
	return parser.get_rate()


@handle_exception(api_logger)
def calculate_usd(amount: float, rate: float) -> Optional[str]:
	try:
		amount = float(amount)
	except (ValueError, TypeError) as e:
		return None
	if not (amount and rate):
		return None
	return str(amount * rate)


class MyHTMLParser(HTMLParser, ABC):
	"""
		Parse HTML page to find the first value inside the tag with special parameters
		:param tag: tag in which we search (e.g. 'div')
		:param param: parameter inside the tag (e.g. 'class')
		:param value: value of the parameter above (class=...)
	"""
	def __init__(self, tag: str, param: str, value: str, *arg: Any, **kwargs: Any) -> None:
		super().__init__(*arg, **kwargs)
		self.caught_flag: bool = False
		self.rates: list[float] = []
		self.tag: str = tag
		self.param: str = param
		self.value: str = value

	def get_rate(self) -> Optional[float]:
		#  Get the first one from all matched
		return self.rates[0] if self.rates else None

	def handle_starttag(self, tag: str, attrs: list[list[str]]):
		if tag == self.tag:
			for attr in attrs:
				if attr[0] == self.param and attr[1] == self.value:
					self.caught_flag = True

	@handle_exception(api_logger)
	def handle_data(self, data: str) -> None:
		if self.caught_flag:
			these_regex: str = r'\d*,\d*'
			pattern: re.Pattern = re.compile(these_regex)
			rate: list[str] = re.findall(pattern, data)
			self.rates.append(float(rate[0].replace(',', '.')))
		self.caught_flag = False


if __name__ == '__main__':
	pass
