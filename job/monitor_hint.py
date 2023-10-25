import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from wpt.wpt import WPT

HINT_TAG = "hints"
NO_HINT_TAG = "nohints"
URLS_FILE = "static/urls.json"

NUM_RUNS = 5

# Tag for origin label: monitor.{hints/nohints}. + name + child_path
LABEL_PREFIX = "monitor.{}."


WPT_API_KEY = os.getenv('WPT_API_KEY')
NUM_WORKER = int(os.getenv('NUM_WORKER', '5'))
BASE_URL = os.getenv('WPT_URL')
LOCATION = "US_EAST_1_T3"
BROWSER = "Viasat Browser"
NETWORK = "LTE"

NO_HINT_CMD = "--prism-hints-disabled"

HINT_CMD_V15 = "--hint_selection=PL_RB_CSS-PL_RB_SCRIPT-PL_PRB_CSS-PL_PRB_SCRIPT-PLH_LCP_IMAGE-PL_LCP_MEDIA-PLH_LINK_IMAGE-PC_VHIGH_CSS-PC_VHIGH_SCRIPT-PL_VHIGH_FONT --disable-user-preload"

HINT_CMD = "--hint-selection=PL_RB_CSS-PL_RB_SCRIPT-PL_PRB_CSS-PL_PRB_SCRIPT-PLH_LCP_IMAGE-PL_LCP_MEDIA-PLH_LINK_IMAGE-PC_VHIGH_CSS-PC_VHIGH_SCRIPT-PL_VHIGH_FONT --link-hints-disabled"

def run_test(url, cmd='', label=''):
    print(f"Running wpt test with label: {label}")

    wpt_instance = WPT(BASE_URL, WPT_API_KEY)
    wpt_instance.run_test(
        url, 
        LOCATION, 
        BROWSER, 
        NETWORK,
        cmd,
        True, 
        True, 
        False,
        label,
        NUM_RUNS
    )

def compare_hints(name, origin, path=''):
    url = origin + path
    label_suffix = name
    if path != '':
        label_suffix += '.' + path

    # run test with no hints
    nohint_label = LABEL_PREFIX.format(NO_HINT_TAG) + label_suffix
    run_test(url, cmd=NO_HINT_CMD, label=nohint_label)

    # run test with hints
    hint_label = LABEL_PREFIX.format(HINT_TAG) + label_suffix
    run_test(url, cmd=HINT_CMD, label=hint_label)

def run():
    if WPT_API_KEY is None or WPT_API_KEY == '':
        print("WPT_API_KEY env variable is not set.")
        exit(1)

    urls = []
    # load urls.json file
    with open(URLS_FILE) as f:
        urls = json.load(f)


    with ThreadPoolExecutor(max_workers=NUM_WORKER) as executor:
        # List to store the future objects of the tasks
        futures = []

        # Submit the tasks (one task for each URL and its children)
        for url in urls:
            name = url['name']
            origin = url['origin']
            futures.append(executor.submit(compare_hints, name, origin))

            for child in url['children']:
                futures.append(executor.submit(compare_hints, name, origin, child))

        # Wait for all tasks to complete and collect their results
        _ = [future.result() for future in as_completed(futures)]
