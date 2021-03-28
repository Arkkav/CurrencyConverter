from main import generate_content, run, generate_response, generate_headers, parse_request
from utils import get_page, MyHTMLParser, calculate_usd
from views import index, return_405, return_404
import config
from unittest import mock, TestCase, main
from urllib.request import urlopen
from threading import Thread
import json
from urllib.error import URLError


class SimplisticTest(TestCase):
	@mock.patch('main.return_405', return_value=3)
	@mock.patch('main.return_404', return_value=2)
	@mock.patch.dict('main.URLS', {'/': lambda y, x: 4})
	def test_generate_content(self, mock_return_404, mock_return_405):
		self.assertTrue(generate_content(200, '/', {'x': 'werf'}, 'header') == 4)
		self.assertTrue(generate_content(404, '/wreg', {'x': 'werf'}, 'header') == ('header', 2))
		self.assertTrue(generate_content(405, '/weg', {'x': 'werf'}, 'header') == ('header', 3))

	@mock.patch('main.generate_response')
	def test_run(self, mock_generate_response):
		json_body = json.dumps({'response': 'good_response'})
		mock_response = ('HTTP/1.1 200 OK\n\n' + json_body).encode()
		mock_generate_response.return_value = mock_response

		# Daemon threads automatically shut down when the main process exits.
		mock_server_thread = Thread(target=run)
		mock_server_thread.setDaemon(True)
		mock_server_thread.start()

		url = 'http://{address}:{port}'.format(address=config.SERVER_ADDRESS, port=config.SERVER_PORT)
		with urlopen(url, timeout=10) as response:
			response_content = response.read()
			response_content = response_content.decode('utf-8')

		# for exiting the main process
		mock_server_thread.do_run = False
		self.assertEqual(response_content, json_body)

	def test_generate_headers(self):
		self.assertEqual(generate_headers('POST', '/'), ('HTTP/1.1 405 Method not allowed\n\n', 405))
		self.assertEqual(generate_headers('GET', '/'), ('HTTP/1.1 200 OK\n\n', 200))
		self.assertEqual(generate_headers('GET', '/ergerg'), ('HTTP/1.1 404 Not found\n\n', 404))

	def test_parse_request(self):
		self.assertEqual(parse_request('GET /?amount=345 HTTP/1.1\r\nConnection: keep-alive'), ('GET', '/', {'amount': '345'}))
		self.assertEqual(parse_request('POST /erger?rate=1 HTTP/1.1\r\nConnection: keep-alive'), ('POST', '/erger', {'rate': '1'}))
		with self.assertRaises(AttributeError):
			parse_request(None)

	def test_get_page(self):
		with self.assertRaises(TypeError):
			code_2, response_content = get_page('https://67j67j67j11112324google.com/')
		code_1 = code_2 = None
		try:
			code_1, response_content = get_page('https://yandex.ru/')
			code_2, response_content = get_page('https://11112324google.com/')
		except Exception:
			pass
		self.assertTrue(200 in (code_1, code_2))

	def test_MyHTMLParser(self):
		content = """
			<div class="main-indicator_rate">
			<div class="col-md-2 col-xs-9 _dollar">USD</div>
			<div class="col-md-2 col-xs-9 _right mono-num">76,1741 ₽
							</div>
			<div class="col-md-2 col-xs-9 _right mono-num">75,7576 ₽
							</div>
			<div class="main-indicator_tooltip" id="V_R01235">
			  <div class="main-indicator_tooltip-footer">Официальный курс Банка России</div>
			</div>
		"""
		parser = MyHTMLParser()
		parser.feed(content)
		self.assertEqual(parser.get_rate(), 76.1741)
		parser = MyHTMLParser()
		content = ''
		parser.feed(content)
		self.assertEqual(parser.get_rate(), None)

	@mock.patch('views.calculate_usd')
	@mock.patch('views.get_rate')
	def test_index(self, mock_get_rate, mock_calculate_usd):
		self.assertEqual(index('headers', amount=''), ('HTTP/1.1 400 Amount parameter not found\n\n', json.dumps({'Error': 'Amount parameter not found.'})))
		mock_get_rate.return_value = None
		self.assertEqual(index('headers', amount='88'), ('HTTP/1.1 500 Bad currency rates service\n\n', json.dumps({'Error': 'Bad currency rates service.'})))
		mock_get_rate.return_value = 42
		mock_calculate_usd.return_value = ''
		self.assertEqual(index('headers', amount='88'), ('HTTP/1.1 400 Amount should be float\n\n', json.dumps({'Error': 'Amount should be float.'})))
		mock_get_rate.return_value = 42
		mock_calculate_usd.return_value = '4'
		self.assertEqual(index('headers', amount='88'), ('headers', json.dumps({'Currency': 'USD', u'Amount': '88', 'Rate': '42', 'Result': '4'})))

	def test_return_405(self):
		self.assertEqual(return_405(), json.dumps({'Error': 'Method not allowed'}))

	def test_return_404(self):
		self.assertEqual(return_404(), json.dumps({'Error': 'Page not found'}))

if __name__ == '__main__':
	main()
