import urllib.request, urllib.parse, urllib.error
import json
import time

class BadRequest(Exception):
    def __init__(self, urllibError):
        self.body = urllibError.read().decode("utf-8")
        super().__init__(f"Bad request sended to the api, check the parameters are correct or your connection\nApi response: {self.body}")


class FlowError(Exception):
    def __init__(self, message):
        super().__init__(message)

fhandler2 = open("HistoryError.txt", "w")

def make_request(url, method_api, data_to_encode):
    if type(data_to_encode) != dict:
        raise TypeError("Data to encode must be a dictionary")
        
    encode_data = urllib.parse.urlencode(data_to_encode)
    url = f"{url}{encode_data}"
    request = urllib.request.Request(url, method=method_api)
    request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
    
    try:
        response = urllib.request.urlopen(request)
    except urllib.error.HTTPError as e:
        raise BadRequest(e)
    
    response_data = response.read()
    decoded = response_data.decode("utf-8")

    json_loaded = json.loads(decoded)
    json_dumped = json.dump(json_loaded, fhandler2, indent=4)
    
    return json_loaded
