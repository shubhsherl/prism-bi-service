import requests
import logging
from bs4 import BeautifulSoup

from helper.file import fetch_from_s3, store_in_s3
from pkg.s3.keys import TOPPAGES_KEY, PREFETCHES_KEY

# Create a logger instance
logger = logging.getLogger('prefetches')

TOPPAGES_FILE_PATH = "static/toppages.json"
PREFETCHES_FILE_PATH = "static/prefetches.json"
DESKTOP_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
PHONE_AGENT = "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.65 Mobile Safari/537.36"

def parse_link_headers(headers):
    link_header_values = headers.get("link", "").split(",")
    preconnect_count = 0
    preload_count = 0

    for link_header_value in link_header_values:
        if "rel=\"preconnect\""  in link_header_value:
            preconnect_count += 1
        elif "rel=\"preload\"" in link_header_value:
            preload_count += 1

    return {
        "preconnect_count": preconnect_count,
        "preload_count": preload_count,
    }

def fetch_hints(url, user_agent):
    headers = {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1",
    }
    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.content, "html.parser")
    preconnect_links = soup.find_all("link", rel="preconnect")
    preload_links = soup.find_all("link", rel="preload")
    header_hints = parse_link_headers(response.headers)

    return {
        "html_preconnects": len(preconnect_links),
        "html_preloads": len(preload_links),
        "http_preconnects": header_hints["preconnect_count"],
        "http_preloads": header_hints["preload_count"],
    }

def fetch_and_analyze_hints(url):
    desktop_hints = fetch_hints(url, DESKTOP_AGENT)
    phone_hints = fetch_hints(url, PHONE_AGENT)

    return {
        "url": url,
        "desktop": desktop_hints,
        "phone": phone_hints,
    }

def run():
    domains = []

    domains = fetch_from_s3(TOPPAGES_KEY)
    if domains is None:
        logger.error(f"Error while fetching urls from {TOPPAGES_KEY}")
        exit(1)

    results = []
    for domain in domains:
        url = 'https://www.' + domain['domain']
        hints = fetch_and_analyze_hints(url)
        results.append(hints)
    
    store_in_s3(PREFETCHES_KEY, results)
