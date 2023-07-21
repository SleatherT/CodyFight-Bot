from api_requests import make_request, FlowError

# Class that allows to execute basic actions and save information
class Client():
    def __init__(self, ckey):
        self.url_api = f"https://game.codyfight.com/?"
        self.ckey = ckey
        self.status = None
        self.jsonResponse = None
        self.get_status()
    
    def get_status(self):
        to_encode = {"ckey": self.ckey}
        info = make_request(url=self.url_api, method_api="GET", data_to_encode=to_encode)
        
        self.jsonResponse = info
        self.status = self.jsonResponse["state"]["status"]
            
        return info
    
    # Creation of room defaults to 0 if not passed
    def create_room(self, mode=0):
        self.get_status()
        if self.status != 1:
            try:
                game_mode = int(mode)
            except:
                raise TypeError("Mode must be a number")
            
            to_encode = {"ckey": self.ckey, "mode": game_mode}
            info = make_request(url=self.url_api, method_api="POST", data_to_encode=to_encode)
            self.jsonResponse = info
            
            print("Room Created!")
            return info
        else:
            raise FlowError("Game already in Course")
        
    def cast_skill(self, x_value, y_value, skill_id=None):
        # Defaults to first skill if not passed, if passed the skill id, this indicates what skill use of the four skill in order, not the unique id of the skill, by 
        # example, swap skill unique id is 5 but from your point of view is probably 1, use his position number since its more convinient
        # If the skill id do not corresponds to any skill raises a IndexError error
        self.get_status()
        if self.status == 1:
            try:
                x_value = int(x_value)
                y_value = int(y_value)
            except:
                raise TypeError("x and y values must be numbers")
            
            listSkills = self.jsonResponse["players"]["bearer"]["skills"]
            if skill_id == None:
                skill_id = listSkills[0]["id"]
            else:
                try:
                    skill_id = listSkills[skill_id]["id"]
                except IndexError:
                    raise IndexError("Skill id do not corresponds to a existing skill")
                    
            to_encode = {"ckey": self.ckey, "skill_id": skill_id, "x": x_value, "y": y_value}
            info = make_request(url=self.url_api, method_api="PATCH", data_to_encode=to_encode)
            self.jsonResponse = info
            
            return info
        else:
            raise FlowError("There is no game in course to cast skill")
        
    def move_player(self, x_value, y_value):
        self.get_status()
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