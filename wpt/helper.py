import string

def format_time(time_value):
    # Converts milliseconds to seconds
    if time_value == "N/A":
        return time_value
    return f"{round(time_value / 1000, 2)}s"

def format_bytes(byte_value):
    # Converts bytes to KiB
    if byte_value == "N/A":
        return byte_value
    return f"{round(byte_value / 1024, 2)} KiB"

def format_float(float_value):
    # Rounds float values to 2 decimal places
    if float_value == "N/A":
        return float_value
    return round(float_value, 2)

def clean_json_text(text):
    printable = set(string.printable)
    cleaned_text = ''.join(char if char in printable else '?' for char in text)
    return cleaned_text