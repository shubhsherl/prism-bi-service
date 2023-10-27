from helper.file import fetch_from_s3
from pkg.s3.keys import RESULTS_KEY

def run():
    data = fetch_from_s3(RESULTS_KEY)
    if data is None:
        return {"success": False, "data": None}
    
    return {"success": True, "data": data}
