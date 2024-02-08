with open('core/openfiles.txt', 'w') as file:
    file.write("openfiles=false")

from strategies.hunterStrategy import strategyPath, strategyAttack, strategySkills, specialStrategyPath, specialStrategyAttack
from core.nodemap import getMap, Graph
from core.client import Client
import json
import time

def GameDebug(jsonResponse):
    print()
    graphObject = Graph(jsonResponse)
    
    print("Player Node: ", graphObject.userNode)
    
    nodeGoal = strategyPath(jsonResponse)
    attack = strategyAttack(jsonResponse)
    skills = strategySkills(jsonResponse)
    specialPath = specialStrategyPath(jsonResponse)
    specialAttack = specialStrategyAttack(jsonResponse, specialPath)
    
    print("ATTACK CONNECTIONS: ", attack)
    print("SKILLS CONNECTIONS: ", skills)
    print("SPECIAL PATH: ", specialPath)
    print("SPECIAL ATTACK", specialAttack)
    print("Node Goal: ", nodeGoal)
    print("Path: ", nodeGoal.pathConnections)
    print("Player Node: ", graphObject.userNode)
    print("Player Life: ", graphObject.userNode.totalLife)
    print("Reviewed Node: ", graphObject.enemyNode)


class UIDebug():
    def __init__(self, debugGames=True, selectLastMaps=False, fastDisplay=True):
        self.specificMap = None
        self.jsonResponses = None
        self.debugGames = debugGames
        self.selectLastMaps = selectLastMaps
        self.fastDisplay = fastDisplay
        
        print(f"\n Configuration:\n debugGames = {self.debugGames} \n selectLastMaps = {self.selectLastMaps}")
        
        actionId = input("\n 0: Save list of maps by id, round and turns (from, to) of history file \n 1: Print Maps of history or testmap \n 2: Print saved maps file \n")
        
        try:
            actionId = int(actionId)
        except ValueError as e:
            raise Exception(f"Input must be a number, details: {e}")
        
        if actionId == 0:
            self.saveMapsOption()
        elif actionId == 1:
            self.printMapsOption()
        elif actionId == 2:
            self.printSavedMapsOp()
        else:
            raise Exception("No valid option")
    
    def saveMapsOption(self):
        fhandlerH = open("misc/history.txt", "r")
        self.jsonResponses = json.load(fhandlerH)
        
        userSearchId = input("ID : \n")
        userRoundId = input("ROUND : \n")
        userFromTurnsId = input("FROM TURN : (ENTER IF YOU WANT TO SAVE FROM THE START)\n")
        userToTurnsId = input("TO TURN : (ENTER IF YOU WANT TO SAVE UNTIL THE LAST)\n")
        
        if len(userFromTurnsId) == 0:
            userFromTurnsId = 0
        else:
            userFromTurnsId = int(userFromTurnsId)
        
        if len(userToTurnsId) == 0:
            # This works but idk
            userToTurnsId = 100
        else:
            userToTurnsId = int(userToTurnsId) + 1
        
        searchList = [jsonResponse for jsonResponse in self.jsonResponses if jsonResponse['state']['id'] == int(userSearchId) and jsonResponse['state']['round'] == int(userRoundId) and jsonResponse['players']['bearer']['turn'] in range(userFromTurnsId, userToTurnsId)]
        if len(searchList) == 0:
            print("No map with that id or turn found")
        else:
            fhandlerS = open("misc/savedMaps.txt", "w")
            json.dump(searchList, fhandlerS, indent=4)
    
    def printSavedMapsOp(self):
        fhandler = open("misc/savedMaps.txt", "r")
        self.jsonResponses = json.load(fhandler)
        self.fastDisplay = False
        self.printMaps()
    
    def printMapsOption(self):
        selectedFile = input("\nUse testmaps file? (Rejecting will use the history file) \n y / n   (ENTER = n)\n")
        
        if selectedFile == "y":
            print("Opening...")
            fhandler = open("misc/testmaps.txt", "r")
            self.jsonResponses = json.load(fhandler)
        elif selectedFile == "n" or len(selectedFile) == 0:
            print("Opening...")
            fhandler = open("misc/history.txt", "r")
            self.jsonResponses = json.load(fhandler)
        else:
            raise ValueError("input y or n (enter is equal to 'n')")
            
        userSearchId = input("ID? \n")
        if len(userSearchId) < 2:
            self.printMaps()
        else:
            userRoundId = input("ROUND? \n")
            self.specificSearch(userSearchId, userRoundId)
    
    def specificSearch(self, userSearchId, userRoundId):
        searchList = [jsonResponse for jsonResponse in self.jsonResponses if jsonResponse['state']['id'] == int(userSearchId) and jsonResponse['state']['round'] == int(userRoundId)]
        if len(searchList) == 0:
            print("No map with that id found")
        else:
            if self.selectLastMaps:
                lenList = len(searchList)
                if lenList < 3:
                    lenList = 3
                
                searchList = searchList[lenList-3:]
            
            self.printMaps(searchList)
    
    def printMaps(self, customList=None):
        if customList is None:
            jsonResponses = self.jsonResponses
        else:
            jsonResponses = customList
        
        if self.fastDisplay is True:
            previousId = None
            previousRound = None
            for jsonResponse in jsonResponses:
                currentId = jsonResponse['state']['id']
                currentRound = jsonResponse['state']['round']
                
                if previousId != currentId:
                    self.printJsonInfo(jsonResponse)
                    previousId = currentId
                    previousRound = currentRound
                elif previousId == currentId and previousRound != currentRound:
                    self.printJsonInfo(jsonResponse)
                    previousId = currentId
                    previousRound = currentRound
                
        else:
            for jsonResponse in jsonResponses:
                self.printJsonInfo(jsonResponse)
    
    def printJsonInfo(self, jsonResponse):
        jsonMapIdData = f"\nID: {jsonResponse['state']['id']}  ROUND: {jsonResponse['state']['round']}  STATUS: {jsonResponse['state']['status']}, PLAYER TURN: {jsonResponse['players']['bearer']['turn']} IS HIS TURN?: {jsonResponse['players']['bearer']['is_player_turn']} ENEMY TURN: {jsonResponse['players']['opponent']['turn']} IS HIS TURN?: {jsonResponse['players']['opponent']['is_player_turn']}"
        print(jsonMapIdData)
        
        if self.debugGames is True and jsonResponse["state"]["status"] == 1:
            player = Client(ckey=None)
            player.jsonResponse = jsonResponse
            player.status = 1
            player.displayInfo()
            GameDebug(jsonResponse)
        else:
            print(getMap(jsonResponse))
        #time.sleep(2)

UIDebug(debugGames=True, fastDisplay=True)