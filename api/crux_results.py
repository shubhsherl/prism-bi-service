from helper.file import fetch_from_s3
from pkg.s3.keys import CRUX_RESULTS_KEY

def run():
    data = fetch_from_s3(CRUX_RESULTS_KEY)
    if data is None:
        return {"success": False, "data": None}
    
    return {"success": True, "data": data}
