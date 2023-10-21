from helper.file import read_json_file

TEST_RESULTS_FILE_PATH = './static/crux_results.json'

def run():
    data = read_json_file(TEST_RESULTS_FILE_PATH)
    if data is None:
        return {"success": False, "data": None}
    
    return {"success": True, "data": data}
