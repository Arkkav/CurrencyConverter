import json
from abc import ABC
from urllib.request import urlopen
import re
from html.parser import HTMLParser
import unittest


class MyHTMLParser(HTMLParser, ABC):
	def __init__(self, *arg, **kwargs):
		super().__init__(*arg, **kwargs)
		self.f = False
		self.usd_rate = []
		
	def get_usd_rate(self):
		return self.usd_rate[0]
		
	def handle_starttag(self, tag, attrs):
		for attr in attrs:
			if attr[0] == 'class' and attr[1] == 'col-md-2 col-xs-9 _right mono-num':
				self.f = True
	
	def handle_endtag(self, tag):
		pass
	
	def handle_data(self, data):
		if self.f:
			these_regex = r'\d*,\d*'
			pattern = re.compile(these_regex)
			titles = re.findall(pattern, data)
			self.usd_rate.append(float(titles[0].replace(',', '.')))
		self.f = False


with urlopen("https://www.cbr.ru/") as response:
	response_content = response.read().decode('utf-8')
	# print(response_content)
	parser = MyHTMLParser()
	parser.feed(response_content)
	print(parser.get_usd_rate())
