from pathlib import Path

import requests
from bs4 import BeautifulSoup
import time


class SciHub:
    def __init__(self, doi: str, path: Path, url='https://sci-hub.se/', timeout=60):
        self.url = url
        self.timeout = timeout
        self.path = path
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
        }
        self.payload = {
            'sci-hub-plugin-check': '',
            'request': str(doi)
        }

    def _send_request(self):
        res = requests.post(self.url, headers=self.headers, data=self.payload, timeout=self.timeout)
        assert res.ok, 'Failed to fetch %s, status code: %d' % (self.url, res.status_code)
        time.sleep(5)
        return res

    def _extract_url(self, response):
        soup = BeautifulSoup(response.content, 'html.parser')
        try:
            content_url = soup.find(id='pdf').get('src').replace('#navpanes=0&view=FitH', '').replace('//', '/')
            if not content_url.endswith('.pdf'):
                raise AttributeError()
        except AttributeError:
            print("Failed to find ", self.payload['request'])
            return

        if content_url.startswith('/downloads'):
            return 'https://sci-hub.se' + content_url
        elif content_url.startswith('/tree'):
            return 'https://sci-hub.se' + content_url
        elif content_url.startswith('/uptodate'):
            return 'https://sci-hub.se' + content_url
        else:
            return 'https:/' + content_url

    def fetch(self):
        response = self._send_request()
        pdf_url = self._extract_url(response)
        if pdf_url is None:
            return

        pdf_name = pdf_url.split('/')[-1]
        self.path.joinpath(pdf_name).write_bytes(requests.get(pdf_url).content)
        print("Downloaded %s" % pdf_name)