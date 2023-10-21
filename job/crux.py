import os
import json
import requests

# Set the API key.
CRUX_API_KEY = os.getenv('CRUX_API_KEY')
CRUX_RESULTS_FILE = "static/crux_results.json"

URLS_FILE = "static/urls.json"

def fetch_crux_data(url):
    # Construct the request URL.
    crux_url = "https://chromeuxreport.googleapis.com/v1/records:queryRecord?key={}".format(CRUX_API_KEY)
    
    # Construct the request body.
    request_body = {
        "url": url,
        "formFactor": "DESKTOP",
        "metrics": ["largest_contentful_paint"]
    }

    # Send the request.
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    response = requests.post(
        crux_url,
        headers=headers,
        data=json.dumps(request_body)
    )

    if response.status_code != 200:
        print(f"Error while fetching CrUX data for {url}: {response.status_code}")
        return

    # Parse the response.
    data = response.json()
    return parse_response(url, data)

def parse_response(url, data):
    if 'record' not in data or 'metrics' not in data['record'] or 'largest_contentful_paint' not in data['record']['metrics']:
        print(f"Error while parsing CrUX data for {url}: no record found")
        return
    
    lcp = {
        'p75': data['record']['metrics']['largest_contentful_paint']['percentiles']['p75'],
    }

    for item in data['record']['metrics']['largest_contentful_paint']['histogram']:
        density = item['density'] * 100
        if item['start'] == 0:
            lcp['good'] = density
        elif item['start'] == 2500:
            lcp['average'] = density
        else:
            lcp['bad'] = density
    
    return {
        'url': url,
        'lcp': lcp,
    }

def run():
    if CRUX_API_KEY is None or CRUX_API_KEY == '':
        print("CRUX_API_KEY env variable is not set.")
        exit(1)

    urls = []
    # load urls.json file
    with open(URLS_FILE) as f:
        urls = json.load(f)

    reports = []
    # loop over urls and fetch Crux data
    for url in urls:
        origin = url['origin']
        
        data = fetch_crux_data(origin)
        if data is not None:
            reports.append(data)

        for child in url['children']:
            data = fetch_crux_data(origin+child)
            if data is not None:
                reports.append(data)

    # write results to file
    with open(CRUX_RESULTS_FILE, 'w') as f:
        json.dump(reports, f, indent=4)
