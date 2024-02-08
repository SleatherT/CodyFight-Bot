from config import SAVEHISTORY
import urllib.request, urllib.parse, urllib.error
import json
import time
import datetime
import http.client

from core.nodemap import AttackSKill, MovementSkill, getMap
#from core.simulator import 

fhandler = None
fhandler = None
fhandlerLogs = None

with open('core/openfiles.txt', 'r') as file:
    content = file.read()
    confirmation = content[10:]
    if confirmation == 'true':
        fhandler = open("misc/history.txt", "w")
        fhandler = open("misc/history.txt", "r+")
        fhandler.write("[")
        fhandlerLogs = open("misc/connection_errors.txt", "w")

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

# Class that allows to execute basic actions and save information
class Client():
    def __init__(self, ckey, multiProcessing=False, displayActions=True):
        self.url_api = f"https://game.codyfight.com/?"
        self.ckey = ckey
        self.status = None
        self.jsonResponse = None
        self.displayActions = displayActions
        
        self.saveReq = True
        if multiProcessing is True:
            self.saveReq = False
    
    # The main function to send requests to the api
    def make_request(self, url, method_api, data_to_encode):
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
        
        if self.saveReq is True and SAVEHISTORY is True:
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
            self.jsonResponse = json_loaded
            self.status = self.jsonResponse["state"]["status"]
            
            json_dumped = json.dumps(json_loaded, indent=4)
            fhandler.write(json_dumped)
            fhandler.write("]")
        else:
            json_loaded = json.loads(decoded)
            self.jsonResponse = json_loaded
            self.status = self.jsonResponse["state"]["status"]
    
        return json_loaded
    
    
    def get_status(self):
        to_encode = {"ckey": self.ckey}
        info = self.make_request(url=self.url_api, method_api="GET", data_to_encode=to_encode)
        
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
                self.make_request(url=self.url_api, method_api="POST", data_to_encode=to_encode)
            elif mode == 1 and opponent_name is not None:
                to_encode = {"ckey": self.ckey, "mode": game_mode, "opponent": opponent_name}
                self.make_request(url=self.url_api, method_api="POST", data_to_encode=to_encode)
            elif mode == 3:
                to_encode = {"ckey": self.ckey, "mode": game_mode}
                self.make_request(url=self.url_api, method_api="POST", data_to_encode=to_encode)
            else:
                raise FlowError("Mode not supported or wrong arguments!")
                
            
            print("Room Created!")
            time.sleep(0.7)
            return self.jsonResponse
        else:
            raise FlowError("Game already in Course")
    
    # If passed a connection to cast the skill, it will use it even if x and y values were provided
    def cast_skill(self, x_value=None, y_value=None, skill_id=None, connection=None):
        if self.status == 1 and connection is None:
            try:
                x_value = int(x_value)
                y_value = int(y_value)
            except:
                raise TypeError("x and y values must be numbers")
                    
            to_encode = {"ckey": self.ckey, "skill_id": skill_id, "x": x_value, "y": y_value}
            self.make_request(url=self.url_api, method_api="PATCH", data_to_encode=to_encode)
            
            if self.displayActions:
                print(f"\nUSING SKILL, ID: {skill_id}")
            
            return self.jsonResponse
        elif self.status == 1 and connection is not None:
            coords = connection.positionTo
            
            to_encode = {"ckey": self.ckey, "skill_id": connection.idSkill, "x": coords["x"], "y": coords["y"]}
            self.make_request(url=self.url_api, method_api="PATCH", data_to_encode=to_encode)
            
            if self.displayActions:
                if type(connection) is MovementSkill:
                    print(f"\nUSING MOVEMENT SKILL: {connection.nameSkill}")
                elif type(connection) is AttackSKill:
                    objectiveNode = connection.nodeTo
                    print(f"\nATTACKING: {connection.nameSkill}  DAMAGE: {connection.damage} OBJECTIVE: {objectiveNode.nameNode} OBJECTIVE LIFE: {objectiveNode.totalLife}")
                else:
                    print(f"\nUSING SKILL: {connection.nameSkill}")
            
            return self.jsonResponse
            
        else:
            raise FlowError("There is no game in course to cast skill")
        
    def move_player(self, x_value=None, y_value=None, connection=None):
        if self.status == 1 and connection is None:
            try:
                x_value = int(x_value)
                y_value = int(y_value)
            except:
                raise TypeError("x and y values must be numbers")
        
            to_encode = {"ckey": self.ckey, "x": x_value, "y": y_value}
            self.make_request(url=self.url_api, method_api="PUT", data_to_encode=to_encode)
            
            if self.displayActions:
                print(f"\nMOVING TO x:{x_value} y:{y_value}")
        
            return self.jsonResponse
        elif self.status == 1 and connection is not None:
            coords = connection.positionTo
            
            to_encode = {"ckey": self.ckey, "x": coords["x"], "y": coords["y"]}
            self.make_request(url=self.url_api, method_api="PUT", data_to_encode=to_encode)
            
            if self.displayActions:
                print(f"\nMOVING TO x:{coords['x']} y:{coords['y']}")
        else:
            raise FlowError("There is no game in course to move player")
        
    def surrender(self):
        to_encode = {"ckey": self.ckey}
        info = self.make_request(url=self.url_api, method_api="DELETE", data_to_encode=to_encode)
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
    
    def getLife(self, ofPlayer=True):
        if ofPlayer:
            return self.jsonResponse["players"]["bearer"]["stats"]["hitpoints"]
        else:
            return self.jsonResponse["players"]["opponent"]["stats"]["hitpoints"]
    
    def getArmor(self, ofPlayer=True):
        if ofPlayer:
            return self.jsonResponse["players"]["bearer"]["stats"]["armor"]
        else:
            return self.jsonResponse["players"]["opponent"]["stats"]["armor"]
    
    def getEnergy(self, ofPlayer=True):
        if ofPlayer:
            return self.jsonResponse["players"]["bearer"]["stats"]["energy"]
        else:
            return self.jsonResponse["players"]["opponent"]["stats"]["energy"]
        
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
        
    def displayInfo(self):
        finalStr = getMap(self.jsonResponse)
        if self.status == 1:
            finalStr = f"\n{finalStr}PLAYER LIFE: {self.getLife()} ARMOR: {self.getArmor()} ENERGY: {self.getEnergy()}"
            finalStr = f"{finalStr}\nSKILLS: {self.getSkills()}"
            finalStr = f"{finalStr}\nENEMY LIFE: {self.getLife(ofPlayer=False)} ARMOR: {self.getArmor(ofPlayer=False)} ENERGY: {self.getEnergy(ofPlayer=False)}"
        
        print(finalStr)
    
    def findPath(self):
        pass
