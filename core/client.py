import urllib.request, urllib.parse, urllib.error
import json
import time
import datetime
import http.client

fhandler = open("history.txt", "w")
fhandler = open("history.txt", "r+")
fhandler.write("[")
fhandlerLogs = open("connection_errors.txt", "w")

class BadRequest(Exception):
    def __init__(self, urllibError):
        self.body = urllibError.read().decode("utf-8")
        super().__init__(f"Bad request sended to the api, check the parameters are correct\nApi response: {self.body}")

class ConnectionError(Exception):
    def __init__(self, urllibError):
        errMsg = f"A urllib.error.URLError has ocurred and it was not possible to resolve it, details: {urllibError}"
        super().__init__(errMsg)
        fhandlerLogs.write(f"{current_time}{errMsg}")

class FlowError(Exception):
    def __init__(self, message):
        super().__init__(message)

# The main function to send requests to the api
def make_request(url, method_api, data_to_encode):
    if type(data_to_encode) != dict:
        raise TypeError("Data to encode must be a dictionary")
        
    encode_data = urllib.parse.urlencode(data_to_encode)
    url = f"{url}{encode_data}"
    request = urllib.request.Request(url, method=method_api)
    request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
    
    rTimes = 9
    for n in range(rTimes):
        try:
            response = urllib.request.urlopen(request)
        except urllib.error.HTTPError as e:
            # Testing server errors handling
            if e.code >= 500:
                errMsg = f"\nWARNING: SERVER ERROR, waiting and sending again the request"
                current_time = datetime.datetime.now()
                print(errMsg)
                fhandlerLogs.write(f"{current_time}{errMsg}")
                time.sleep(40),
                if n < rTimes - 1:
                    continue
                else:
                    raise ConnectionError(e)
            else:
                raise BadRequest(e)
        # Testing except block for connection errors
        except urllib.error.URLError as e:
            errMsg = f"\nWARNING: Opening the url of the api failed, this may be caused by connection issues or the url is invalid, waiting and sending again the request!\nDetails:{e}"
            current_time = datetime.datetime.now()
            print(errMsg)
            fhandlerLogs.write(f"{current_time}{errMsg}")
            time.sleep(5)
            if n < rTimes - 1:
                continue
            else:
                raise ConnectionError(e)
        # Testing another server error handling
        except http.client.RemoteDisconnected as e:
            errMsg = f"\nWARNING: SERVER DISCONNECTED \nDetails:{e}"
            current_time = datetime.datetime.now()
            print(errMsg)
            fhandlerLogs.write(f"{current_time}{errMsg}")
            time.sleep(40)
            if n < rTimes - 1:
                continue
            else:
                raise ConnectionError(e)
        break
    
    response_data = response.read()
    decoded = response_data.decode("utf-8")
    
    fhandler.seek(0)
    # Deleting previous "]" character
    fhandler.seek(0, 2)
    pointer = fhandler.tell()
    fhandler.seek(pointer - 1)
    lastChar = fhandler.read()
    if lastChar == "]":
        fhandler.seek(pointer - 1)
        fhandler.write(",")
    
    json_loaded = json.loads(decoded)
    json_dumped = json.dumps(json_loaded, indent=4)
    fhandler.write(json_dumped)
    fhandler.write("]")
    
    return json_loaded

# Class that allows to execute basic actions and save information
class Client():
    def __init__(self, ckey):
        self.url_api = f"https://game.codyfight.com/?"
        self.ckey = ckey
        self.status = None
        self.jsonResponse = None
    
    def get_status(self):
        to_encode = {"ckey": self.ckey}
        info = make_request(url=self.url_api, method_api="GET", data_to_encode=to_encode)
        
        self.jsonResponse = info
        self.status = self.jsonResponse["state"]["status"]
            
        return info
    
    # Creation of room defaults to 0 if not passed
    def create_room(self, mode=0, opponent_name=None):
        if self.status != 1:
            try:
                game_mode = int(mode)
            except:
                raise TypeError("Mode must be a number")
            
            if mode == 0 and opponent_name is None:
                to_encode = {"ckey": self.ckey, "mode": game_mode}
                info = make_request(url=self.url_api, method_api="POST", data_to_encode=to_encode)
                self.jsonResponse = info
            elif mode == 1 and opponent_name is not None:
                to_encode = {"ckey": self.ckey, "mode": game_mode, "opponent": opponent_name}
                info = make_request(url=self.url_api, method_api="POST", data_to_encode=to_encode)
                self.jsonResponse = info
            elif mode == 3:
                to_encode = {"ckey": self.ckey, "mode": game_mode}
                info = make_request(url=self.url_api, method_api="POST", data_to_encode=to_encode)
                self.jsonResponse = info
            else:
                raise FlowError("Mode not supported or wrong arguments!")
                
            
            print("Room Created!")
            time.sleep(0.7)
            return info
        else:
            raise FlowError("Game already in Course")
        
    def cast_skill(self, x_value, y_value, skill_id=None):
        # Defaults to first skill if not passed, the skill id must be his unique id, not positional id
        if self.status == 1:
            try:
                x_value = int(x_value)
                y_value = int(y_value)
            except:
                raise TypeError("x and y values must be numbers")
            
            listSkills = self.jsonResponse["players"]["bearer"]["skills"]
            if skill_id == None:
                skill_id = listSkills[0]["id"]
                    
            to_encode = {"ckey": self.ckey, "skill_id": skill_id, "x": x_value, "y": y_value}
            info = make_request(url=self.url_api, method_api="PATCH", data_to_encode=to_encode)
            self.jsonResponse = info
            
            return info
        else:
            raise FlowError("There is no game in course to cast skill")
        
    def move_player(self, x_value, y_value):
        if self.status == 1:
            try:
                x_value = int(x_value)
                y_value = int(y_value)
            except:
                raise TypeError("x and y values must be numbers")
        
            to_encode = {"ckey": self.ckey, "x": x_value, "y": y_value}
            info = make_request(url=self.url_api, method_api="PUT", data_to_encode=to_encode)
            self.jsonResponse = info
        
            return info
        else:
            raise FlowError("There is no game in course to move player")
        
    def surrender(self):
        to_encode = {"ckey": self.ckey}
        info = make_request(url=self.url_api, method_api="DELETE", data_to_encode=to_encode)
        self.get_status()
        
        return info
        
    def getIdStatus(self):
        self.get_status()
        return self.status
        
    def getIsPlayerTurn(self):
        return self.jsonResponse["players"]["bearer"]["is_player_turn"]
    
    def getJsonResponse(self):
        return self.jsonResponse
        
    def getWinner(self):
        return self.jsonResponse["verdict"]["winner"]
    
    def getLife(self):
        return self.jsonResponse["players"]["bearer"]["stats"]["hitpoints"]
    
    def getArmor(self):
        return self.jsonResponse["players"]["bearer"]["stats"]["armor"]
    
    def getEnergy(self):
        return self.jsonResponse["players"]["bearer"]["stats"]["energy"]
        
    def getSkills(self):
        finalStr = str()
        for skill in self.jsonResponse["players"]["bearer"]["skills"]:
            if skill["status"] == 1:
                finalStr = f"{finalStr}{skill['name']}   "
            elif skill["status"] == -1:
                finalStr = f"{finalStr}{skill['name']} Not Enough Energy   "
            # Status -2: Skill available but without targets
            elif skill["status"] == -2:
                finalStr = f"{finalStr}{skill['name']}   "
            elif skill["status"] == 0:
                finalStr = f"{finalStr}{skill['name']} In Cooldown   "
        
        return finalStr
