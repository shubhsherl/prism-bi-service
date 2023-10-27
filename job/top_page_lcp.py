import os
import time
import requests
import json
import logging

from helper.file import fetch_from_s3, store_in_s3
from pkg.s3.keys import TOPPAGES_KEY

# Create a logger instance
logger = logging.getLogger('top_page_lcp')

# Set the API key.
CRUX_API_KEY = os.getenv('CRUX_API_KEY')

def fetch_lcp_data(url):
    logger.info(f"Fetching CrUX data for {url}...")
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
        logger.info(f"Retrying after {retry_after} seconds...")
        time.sleep(retry_after)
        return fetch_lcp_data(url)
    elif response.status_code != 200:
        logger.error(f"Error while fetching CrUX data for {url}: {response.status_code}")
        return

    # Parse the response.
    data = response.json()
    return parse_response(url, data)

def parse_response(url, data):
    if 'record' not in data or 'metrics' not in data['record'] or 'largest_contentful_paint' not in data['record']['metrics']:
        logger.error(f"Error while parsing CrUX data for {url}: no record found")
        return
    
    lcp_p75 = data['record']['metrics']['largest_contentful_paint']['percentiles']['p75']
    return lcp_p75


def run():
    if CRUX_API_KEY is None:
        logger.error("CRUX_API_KEY environment variable not set")
        return

    logger.info("Running top pages LCP worker...")

    domains = fetch_from_s3(TOPPAGES_KEY)
    if domains is None:
        logger.error(f"Error while fetching urls from {TOPPAGES_KEY}")
        return

    # Update the JSON with p75 LCP data for each domain
    updated_domains = []
    for domain in domains:
        url = 'https://www.' + domain['domain']
        p75_lcp = fetch_lcp_data(url)
        if p75_lcp is not None:
            domain["p75_lcp"] = p75_lcp
            updated_domains.append(domain)

    # Save the updated JSON to the output file
    store_in_s3(TOPPAGES_KEY, updated_domains)
    logger.info(f"Updated JSON saved to {TOPPAGES_KEY} in S3")
