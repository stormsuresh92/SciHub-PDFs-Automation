import logging
import csv
import time
from pathlib import Path
import requests
from bs4 import BeautifulSoup


class SciHub:
    def __init__(self, doi: str, path: Path, csv_path: Path, log_path: Path, url='https://sci-hub.se/', timeout=60, rate_limit=10):
        self.url = url
        self.timeout = timeout
        self.path = path
        self.csv_path = csv_path
        self.rate_limit = rate_limit  # Time in seconds between requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
        }
        self.payload = {
            'sci-hub-plugin-check': '',
            'request': str(doi)
        }
        
        logging.basicConfig(filename=log_path, level=logging.DEBUG, 
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        self.last_request_time = 0

    def _send_request(self):
        current_time = time.time()
        elapsed_time = current_time - self.last_request_time
        if elapsed_time < self.rate_limit:
            time.sleep(self.rate_limit - elapsed_time)

        try:
            res = requests.post(self.url, headers=self.headers, data=self.payload, timeout=self.timeout)
            res.raise_for_status()
            self.last_request_time = time.time()
            time.sleep(5)
            return res
        except requests.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            return None

    def _extract_url(self, response):
        if response is None:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        try:
            content_url = soup.find(id='pdf').get('src').replace('#navpanes=0&view=FitH', '').replace('//', '/')
            if not content_url.endswith('.pdf'):
                raise AttributeError()
        except AttributeError:
            self.logger.error(f"Failed to find PDF for DOI: {self.payload['request']}")
            return None

        if content_url.startswith('/downloads') or content_url.startswith('/tree') or content_url.startswith('/uptodate'):
            return 'https://sci-hub.se' + content_url
        else:
            return 'https:/' + content_url

    def _save_to_csv(self, doi, pdf_url):
        with open(self.csv_path, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([doi, pdf_url])

    def fetch(self):
        self.logger.info(f"Fetching DOI: {self.payload['request']}")
        response = self._send_request()
        pdf_url = self._extract_url(response)
        
        if pdf_url is None:
            return

        pdf_name = pdf_url.split('/')[-1]
        pdf_path = self.path.joinpath(pdf_name)
        try:
            pdf_content = requests.get(pdf_url).content
            pdf_path.write_bytes(pdf_content)
            self.logger.info(f"Downloaded: {pdf_name}")
            self._save_to_csv(self.payload['request'], pdf_url)
        except requests.RequestException as e:
            self.logger.error(f"Failed to download PDF: {e}")
