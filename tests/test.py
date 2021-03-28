from main import generate_content, run, generate_response
import views
import config
from unittest import mock, TestCase, main
from urllib.request import urlopen
from threading import Thread
import json


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
		mock_server_thread.do_run = False
		self.assertEqual(response_content, json_body)


if __name__ == '__main__':
	main()
