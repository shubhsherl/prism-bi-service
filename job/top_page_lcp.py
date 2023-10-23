import os
import time
import requests
import json

# Set the API key.
CRUX_API_KEY = os.getenv('CRUX_API_KEY')
TOPPAGES_FILE_PATH = "static/toppages.json"

def fetch_lcp_data(url):
    print(f"Fetching CrUX data for {url}...")
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

    if response.status_code == 429:
        # Handle 429 error by waiting and then retrying
        retry_after = int(response.headers.get("Retry-After", 30))
        print(f"Retrying after {retry_after} seconds...")
        time.sleep(retry_after)
        return fetch_lcp_data(url)
    elif response.status_code != 200:
        print(f"Error while fetching CrUX data for {url}: {response.status_code}")
        return

    # Parse the response.
    data = response.json()
    return parse_response(url, data)

def parse_response(url, data):
    if 'record' not in data or 'metrics' not in data['record'] or 'largest_contentful_paint' not in data['record']['metrics']:
        print(f"Error while parsing CrUX data for {url}: no record found")
        return
    
    lcp_p75 = data['record']['metrics']['largest_contentful_paint']['percentiles']['p75']
    return lcp_p75


def run():
    if CRUX_API_KEY is None:
        print("CRUX_API_KEY environment variable not set")
        return

    print("Running top pages LCP worker...")

    domains = []
    # Load the list of domains from the input JSON file
    with open(TOPPAGES_FILE_PATH, "r") as file:
        domains = json.load(file)

    # Update the JSON with p75 LCP data for each domain
    updated_domains = []
    for domain in domains:
        url = 'https://www.' + domain['domain']
        p75_lcp = fetch_lcp_data(url)
        if p75_lcp is not None:
            domain["p75_lcp"] = p75_lcp
            updated_domains.append(domain)

    # Save the updated JSON to the output file
    with open(TOPPAGES_FILE_PATH, "w") as file:
        json.dump(updated_domains, file, indent=4)

    print(f"Updated JSON saved to {TOPPAGES_FILE_PATH}")
