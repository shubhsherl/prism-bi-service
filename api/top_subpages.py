import os
import json
import requests
from googleapiclient.discovery import build
from concurrent.futures import ThreadPoolExecutor, as_completed
from cache.cache import InMemoryCache

API_KEY = os.getenv('API_KEY')
CRUX_API_KEY = os.getenv('CRUX_API_KEY')
CX_ID = os.getenv('CX_ID')
NUM_WORKER=50

cache = InMemoryCache(max_size=100)

def cache_key(url, n):
    return f"{url}-{n}"

def _top_subpages(url, num):
    query = "site:{}".format(url)
    service = build("customsearch", "v1", developerKey=API_KEY)

    results = []
    start = 1
    while start <= num:
        response = service.cse().list(
            q=query,
            cx=CX_ID,
            siteSearch=url,
            siteSearchFilter='i',
            num=min(num - start + 1, 10),    # Maximum number of results is 10
            start=start
        ).execute()
        results.extend(response["items"])
        start += len(response.get("items", []))
        if "nextPage" not in response["queries"]:
            break

    urls = []
    for item in results:
        if 'link' in item:
            urls.append(item['link'])
                
    return urls

def _fetch_lcp_results(urls, crux_key):
    num_workers = min(len(urls), NUM_WORKER)
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        # List to store the future objects of the tasks
        futures = []

        # Submit the tasks (one task for each URL and its children)
        for url in urls:
            futures.append(executor.submit(_fetch_lcp_75_crux, url, crux_key))

        # Wait for all tasks to complete and collect their results
        lcp_data_list = [future.result() for future in as_completed(futures)]
        lcp_data_list = [lcp_data for lcp_data in lcp_data_list if lcp_data['DESKTOP'] is not None and lcp_data['PHONE'] is not None]
        lcp_data_list = sorted(lcp_data_list, key=lambda k: k['DESKTOP'], reverse=True)
        return lcp_data_list

def _fetch_lcp_75_crux(url, crux_key):
    form_factors = ['DESKTOP', 'PHONE']
    lcp_results = {
        'url': url,
        'DESKTOP': None,
        'PHONE': None
    }

    for form_factor in form_factors:
        # Build the CrUX POST data
        crux_api_url = f'https://chromeuxreport.googleapis.com/v1/records:queryRecord?key={crux_key}'
        query_data = {
            "url": url,
            "formFactor": form_factor
        }
        headers = {'Content-type': 'application/json'}

        # Request CrUX data for the URL
        try:
            response = requests.post(crux_api_url, data=json.dumps(query_data), headers=headers)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException:
            print(f"Chrome UX report data not found for {url} ({form_factor})")
            lcp_results[form_factor] = None
            continue

        # Parse the CrUX data to retrieve the LCP value
        if 'record' in data and 'metrics' in data['record']:
            metrics = data['record']['metrics']
            print("url={}.".format(url))
            if 'largest_contentful_paint' in metrics:
                lcp_data = metrics['largest_contentful_paint']
                # Store the 75th percentile value for the form factor
                lcp_results[form_factor] = lcp_data['percentiles']['p75']
        else:
            print(f"Chrome UX report data not found for {url} ({form_factor})")
            lcp_results[form_factor] = None

    return lcp_results

def fetch_from_cache(url, n):
    key = cache_key(url, n)
    if cache.contains(key):
        return cache.get(key), True
    
    return None, False

def set_in_cache(url, n, data):
    key = cache_key(url, n)
    cache.set(key, data)

def run(url, n):
    cache_value, found = fetch_from_cache(url, n)
    if found:
        return {"success": True, "data": cache_value}
    
    top_subpages = _top_subpages(url, n)
    lcp_data_list = _fetch_lcp_results(top_subpages, CRUX_API_KEY)

    data = {
        "url": url,
        "top_subpages": top_subpages,
        "lcp_data": lcp_data_list
    }

    set_in_cache(url, n, data)
    return {"success": True, "data": data}