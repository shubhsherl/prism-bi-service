import os
import logging
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

from wpt.wpt import WPT
import wpt.keys as wpt_keys
from helper.file import fetch_from_s3, store_in_s3
from pkg.s3.keys import RESULTS_KEY, PRISM_DOMAINS_KEY

# Create a logger instance
logger = logging.getLogger('build_report')

MAX_DAYS = 30

NUM_WORKER = int(os.getenv('NUM_WORKER', '10'))
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '100'))

MONITOR_LABEL_PREFIX = "monitor."

BASE_URL = os.getenv('WPT_URL')
WPT_API_KEY = os.getenv('WPT_API_KEY')

monitored_urls = {}

def is_valid_test(result):
    global monitored_urls

    if not result[wpt_keys.KEY_LABEL].startswith(MONITOR_LABEL_PREFIX):
        return False
    
    origin, path = get_base_url(result['URL'])
    found = False
    for murl in monitored_urls:
        if murl['origin'] != origin:
            continue

        if path == '/' or path == '':
            found = True
            break

        if path in murl['children']:
            found = True
            break
    
    if not found:
        return False

    return True

def is_valid_result(result):
    lcp = 0
    if 'average' in result and 'firstView' in result['average'] and 'chromeUserTiming.LargestContentfulPaint' in result['average']['firstView']:
        lcp = result['average']['firstView']['chromeUserTiming.LargestContentfulPaint']
    
    if lcp == 0:
        return False
    
    return True


def get_base_url(url):
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return base_url, parsed_url.path

# fetch results list with label starting with `monitor.` and return test ids
def fetch_results_list():
    wpt_instance = WPT(BASE_URL, WPT_API_KEY)
    results = wpt_instance.list_tests(MAX_DAYS, MONITOR_LABEL_PREFIX, False)
    return [result[wpt_keys.KEY_TEST_ID] for result in results if is_valid_test(result)]

def fetch_results_for_chunk(chunk):
    logger.info(f"Fetching results for {len(chunk)} tests...")
    wpt_instance = WPT(BASE_URL, WPT_API_KEY)
    chunk_results = wpt_instance.get_results(chunk, False)
    valid_results = [parse_result(result) for result in chunk_results if is_valid_result(result)]
    del chunk_results
    return valid_results

def fetch_results():
    result_list = fetch_results_list()
    logger.info(f"Fetching results for {len(result_list)} tests...")
    results = []
    
    with ThreadPoolExecutor(max_workers=NUM_WORKER) as executor:
        # List to store the future objects of the tasks
        futures = []

        # Submit the tasks (one task for each URL and its children)
        for i in range(0, len(result_list), CHUNK_SIZE):
            chunk = result_list[i:i+CHUNK_SIZE]
            futures.append(executor.submit(fetch_results_for_chunk, chunk))

        # Wait for all tasks to complete and collect their results
        results = [future.result() for future in as_completed(futures)]
        results = [item for sublist in results for item in sublist]
    
    return results

def parse_result(result):
    lcp = 0
    if 'average' in result and 'firstView' in result['average'] and 'chromeUserTiming.LargestContentfulPaint' in result['average']['firstView']:
        lcp = result['average']['firstView']['chromeUserTiming.LargestContentfulPaint']
    
    origin, _ = get_base_url(result['testUrl'])
    return {
        'id': result['id'],
        'url': result['testUrl'],
        'timestamp': result['completed'],
        'lcp': lcp,
        'origin': origin,
        'wpt_url': f'{BASE_URL}/result/{result["id"]}',
        'lighthouse_url': f'{BASE_URL}/result/{result["id"]}',
        'label': result['label']
    }

def run():
    global monitored_urls
    monitored_urls = fetch_from_s3(PRISM_DOMAINS_KEY)
    if monitored_urls is None:
        logger.error(f"Error while fetching monitored urls from {PRISM_DOMAINS_KEY}")
        exit(1)

    results = fetch_results()
    store_in_s3(RESULTS_KEY, results)
