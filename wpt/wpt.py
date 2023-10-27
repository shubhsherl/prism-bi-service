import requests
import csv
from io import StringIO
from bs4 import BeautifulSoup
import time
import json
import os
import logging
from prettytable import PrettyTable
from .helper import format_time, format_bytes, format_float, clean_json_text

# Create a logger instance
logger = logging.getLogger('monitor_hint')

class WPT:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key

    def wait_for_test_result(self, test_id, wait):
        while True:
            results_response = requests.get(f"{self.base_url}/jsonResult.php?test={test_id}")
            if results_response.status_code != 200:
                logger.error(f"Error while fetching results: {results_response.text}")
                return

            results_data = json.loads(clean_json_text(results_response.text))
            logger.info(f"Test status for {test_id}: {results_data['statusText']}")
            if results_data['statusCode'] == 200:
                logger.info(f"View results: {results_data['data']['summary']}")
                return results_data

            if not wait:
                return results_data

            time.sleep(30)

    def save_netlogs(self, test_id):
        self.save_netlog(test_id, '1')
        self.save_netlog(test_id, '1_Cached')

    def save_netlog(self, test_id, run='1'):
        # fetches test result and save netlogs in a file: netlog_{test_id}.json
        response = requests.get(f"{self.base_url}/getgzip.php?test={test_id}&file={run}_netlog.txt", stream=True)
        
        if response.status_code != 200:
            logger.error(f"Netlog not found for test: {test_id} {response.text}")
            return
        
        directory = 'netlogs'
        if not os.path.exists(directory):
            os.makedirs(directory)

        file_name = f'{directory}/{test_id}_netlog_{run}.json'
        try:
            os.remove(file_name)
        except FileNotFoundError:
            pass

        with open(file_name, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info(f"Netlog file saved in {directory}/{test_id}_netlog_{run}.json")

    def run_test(self, url, location, browser, network, command_line, filmstrip, wait, netlogs=False, label='', runs=1):
        params = {
            'k': self.api_key,
            'url': url,
            'location': f"{location}:{browser}.{network}",
            'f': 'json',
            'cmdline': command_line,
            'fvonly': '1',
            'runs': runs,
            'stopAtDocumentComplete': '1',
            'lighthouse': '1',
            'label': label
        }

        if netlogs:
            params['netlog'] = '1'

        if filmstrip:
            params['video'] = '1'

        logger.info(f"Running test for {url} on {network} in {browser} at {location}...")
        response = requests.get(f"{self.base_url}/runtest.php", params=params)
        if response.status_code != 200:
            logger.error(f"Error while running test: {response.text}")
            return
        
        data = response.json()

        if data['statusCode'] != 200:
            logger.error(f"Error: {data['statusText']}")
            return

        test_id = data['data']['testId']
        logger.info(f"Test started with ID: {test_id}")

        if wait:
            test_result = self.wait_for_test_result(test_id, wait)
            average_result = test_result['data']['average']
            average_result['id'] = test_id
            self.pretty_print([average_result])

            if netlogs:
                self.save_netlogs(test_id)

            return test_result
        
        return data['data']

    def list_tests(self, days=1, filter='', print_table=True):
        endpoint = f"{self.base_url}/testlog.php?days={days}&nolimit=1&filter={filter}&all=on&k={self.api_key}&f=csv"
        response = requests.get(endpoint)
        if response.status_code != 200:
            logger.error(f"Error while fetching tests list: {response.text}")
            return

        data = response.text

        # Using StringIO to emulate a file object for the given string
        csv_file = StringIO(data)

        # Parsing CSV content
        reader = csv.reader(csv_file)
        headers = next(reader)

        results = []
        # Initialize the table with headers
        table = PrettyTable(headers)
        # Add rows to the table
        for row in reader:
            # Strip HTML from the 'Location' column
            row[1] = BeautifulSoup(row[1], "html.parser").get_text()
            table.add_row(row)
            row_dict = {headers[i]: row[i] for i in range(len(headers))}
            results.append(row_dict)
        
        if print_table:
            logger.info(table)

        return results

    def get_results(self, test_ids, wait, netlogs=False, print_data=False):
        logger.info(f"Fetching results for {len(test_ids)} tests...")
        avg_results = []
        results = []
        for test_id in test_ids:
            results_data = self.wait_for_test_result(test_id, wait)
            if results_data['statusCode'] != 200:
                continue        
            
            if netlogs:
                self.save_netlogs(test_id)

            average_result = results_data['data']['average']
            average_result['id'] = test_id
            avg_results.append(results_data['data']['average'])
            results.append(results_data['data'])

        if print_data:
            logger.info(f"Comparison link: {self.base_url}/video/compare.php?tests={','.join(test_ids)}")
            self.pretty_print(avg_results)
        return results
    
    def pretty_print(self, test_results):
        if len(test_results) == 0:
            return
        
        headers = [
            "ID", "View", "First Byte", "Start Render", "FCP",
            "LCP", "CLS", "TBT",
            "FLT", "FLR", "FL Bytes In"
        ]

        table = PrettyTable(field_names=headers)

        for result in test_results:
            first_view = result['firstView']

            if not isinstance(first_view, dict):
                continue

            table.add_row([
                result['id'],
                "First View",
                format_time(first_view.get('TTFB', "N/A")),
                format_time(first_view.get('render', "N/A")),
                format_time(first_view.get('firstContentfulPaint', "N/A")),
                format_time(first_view.get('chromeUserTiming.LargestContentfulPaint', "N/A")),
                format_float(first_view.get('chromeUserTiming.CumulativeLayoutShift', "N/A")),
                format_time(first_view.get('TotalBlockingTime', "N/A")),
                format_time(first_view.get('fullyLoaded', "N/A")),
                format_float(first_view.get('requestsFull', "N/A")),
                format_bytes(first_view.get('bytesIn', "N/A"))
            ])

            if 'repeatView' not in result:
                continue

            repeat_view = result['repeatView']

            if not isinstance(repeat_view, dict):
                continue
            
            table.add_row([
                result['id'],
                "Repeat View",
                format_time(repeat_view.get('TTFB', "N/A")),
                format_time(repeat_view.get('render', "N/A")),
                format_time(repeat_view.get('firstContentfulPaint', "N/A")),
                format_time(repeat_view.get('chromeUserTiming.LargestContentfulPaint', "N/A")),
                format_float(repeat_view.get('chromeUserTiming.CumulativeLayoutShift', "N/A")),
                format_time(repeat_view.get('TotalBlockingTime', "N/A")),
                format_time(repeat_view.get('fullyLoaded', "N/A")),
                format_float(repeat_view.get('requestsFull', "N/A")),
                format_bytes(repeat_view.get('bytesIn', "N/A"))
            ])

        logger.info(table)

    def compare(self, urls, location, browser, network_types, command_line=None, filmstrip=False, wait=False):
        test_ids = []
        for url in urls:
            for network in network_types:
                response = self.run_test(url, location, browser, network, command_line=command_line, filmstrip=filmstrip, wait=wait)
                if response is None:
                    continue
                
                test_id = response["testId"]  # Adjust as needed
                test_ids.append(test_id)

        if wait:
            self.get_results(test_ids, compare=True, print_data=True)
        else:
            logger.info(f"Comparison link: {self.base_url}/video/compare.php?tests={','.join(test_ids)}")
            logger.info("Results will be available once the tests are complete.")
            logger.info(f"Run script: python run.py result -i {' '.join(test_ids)}")
