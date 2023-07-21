import copy
import random

class Graph():
    def __init__(self, jsonResponse):
        playersPosition = jsonResponse["players"]
        agentsPosition = jsonResponse["special_agents"]
        self.skillStatus = jsonResponse["players"]["bearer"]["skills"][0]["status"]
        self.skill = jsonResponse["players"]["bearer"]["skills"][0]["name"]
        
        self.mapList = jsonResponse["map"]
        self.nodesDict = dict()
        self.idGoal = list()
        self.idUser = None
        self.idEnemy = None
        self.idRyo = None
        self.idKix = None
        self.idLlama = None
        self.idRipper = None
        self.idBuzz = None
        self.idListAgents = None
        self.fullListAgents = list()
        self.fullDictAgents = dict()
        self.bidirectionalConnectionsList = list()
        self.userCell = None
        # A special map only to use in the converter function for asigning the types to the nodes
        self.mapDict = dict()
        for lineList in self.mapList:
            for cell in lineList:
                cellId = cell["id"]
                self.mapDict[cellId] = cell
        
        # Call function to save ids
        self.saveIds(playersPosition, agentsPosition)
        cellList = list()
        for lineList in self.mapList:
            for cell in lineList:
                cellList.append(cell)
        
        
        self.bidirectional_tile_flag = False
        firstIterBi_Flag = False
        firstBiCell = None
        secondBiCell = None
        idFirstBiCell = None
        idSecondBiCell = None
        
        # Creating a pre-nodesdict
        for cell in cellList:
            type = cell["type"]
            name = cell["id"]
            # IMPORTANT: Adding the valid cell to the nodesDict, this doesnt mean is going to have connections so there is the possibility of having node objects without a list,
            # This is one of the last modifications of the function so its not debuged
            if type == 0 or type == 2 or type == 4 or type == 5 or type == 6 or type == 7 or type == 8 or type == 9 or type == 10 or type == 11 or type == 13 or type == 15:
                self.nodesDict[name] = list()
                
        # IMPORTANT: This loop creates a dict with "nodes" and his connections from the map, (This doesnt create Nodes objects, dont be confused, since creating the Node 
        # objects require that all connections are registered this code each itireration adds a key, that is the id of the Node, and the value, that is a list 
        # of connection objects to the nodesDict variable, the creation of Node objects is made in the strategyPath() function)
        for cell in cellList:
            slider_tile_flag = False
            type = cell["type"]
            positionCell = cell["position"]
            line = positionCell["y"]
            column = positionCell["x"]
            name = cell["id"]
            # NOTE: If the operator can destroy obstacles this code makes useless his ability since it doesnt takes it as node (a path), this for now i will
            # leave like this since i am using other operator and i dont want to work on it either for now, if someone its going to use a operator that destroy walls 
            # modify this code to check if after destroying the wall there is not another wall, so it can be considered a node (path), good luck btw that looks kinda hard
            if type == 1 or type == 3 or type == 12 or type == 14 or type == 17:
                continue
            elif type == 0 or type == 2 or type == 4 or type == 5 or type == 6 or type == 7 or type == 8 or type == 9 or type == 10 or type == 11 or type == 13 or type == 15:
                pass
            else:
                print(f"Unknown Tile! type: {type} More info: {cell}")
                
            if type == 11:
                confirmation = cell["config"]["is_charged"]
                if firstIterBi_Flag is False:
                    firstBiCell = cell
                else:
                    secondBiCell = cell
                if confirmation == True:
                    firstIterBi_Flag = True
                    self.bidirectional_tile_flag = True
            
            if type == 7 or type == 8 or type == 9 or type == 10:
                confirmation = cell["config"]["is_charged"]
                if confirmation == True:
                    slider_tile_flag = True
            
            
            x_flag = False
            y_flag = False
            
            connectionsList = list()
            connectionsListNextNode = list()
            # Checking y axis next cell
            currentColumnList = self.mapList[column]
            try:
                nextCell = currentColumnList[line + 1]
            except:
                nextCell = None
            
            if nextCell is None:
                pass
            else:
                nameNextCell = nextCell["id"]
                typeNextCell = nextCell["type"]
                positionNextCell = nextCell["position"]
                next_slider_tile_flag = False
                if typeNextCell == 7 or typeNextCell == 8 or typeNextCell == 9 or typeNextCell == 10:
                    confirmation = nextCell["config"]["is_charged"]
                    if confirmation == True:
                        next_slider_tile_flag = True
                if type == 7 or type == 8 or type == 9 or type == 10 and slider_tile_flag:
                    if type == 8:
                        if typeNextCell == 1 or typeNextCell == 3 or typeNextCell == 12  or typeNextCell == 14 or typeNextCell == 17:
                            pass
                        elif typeNextCell == 7 and next_slider_tile_flag:
                            connection = Connection(0, name, nameNextCell, positionCell, positionNextCell)
                            connection2 = Connection(0, nameNextCell, name, positionNextCell, positionCell)
                            connectionsList.append(connection)
                            connectionsListNextNode.append(connection2)
                            y_flag = True
                        elif typeNextCell == 8 or typeNextCell == 9 or typeNextCell == 10 and next_slider_tile_flag:
                            connection = Connection(0, name, nameNextCell, positionCell, positionNextCell)
                            connectionsList.append(connection)
                            y_flag = True
                        else:
                            connection = Connection(0, name, nameNextCell, positionCell, positionNextCell)
                            connection2 = Connection(1, nameNextCell, name, positionNextCell, positionCell)
                            connectionsList.append(connection)
                            connectionsListNextNode.append(connection2)
                            y_flag = True
                    else:
                        if typeNextCell == 1 or typeNextCell == 3 or typeNextCell == 12  or typeNextCell == 14 or typeNextCell == 17:
                            pass
                        elif typeNextCell == 7 and next_slider_tile_flag:
                            connection2 = Connection(0, nameNextCell, name, positionNextCell, positionCell)
                            connectionsListNextNode.append(connection2)
                            y_flag = True
                        elif typeNextCell == 7 or typeNextCell == 8 or typeNextCell == 10 and next_slider_tile_flag:
                            pass
                        else:
                            connection2 = Connection(1, nameNextCell, name, positionNextCell, positionCell)
                            connectionsListNextNode.append(connection2)
                            y_flag = True
                        
                else:
                    if typeNextCell == 1 or typeNextCell == 3 or typeNextCell == 12  or typeNextCell == 14 or typeNextCell == 17:
                        pass
                    elif typeNextCell == 7 and next_slider_tile_flag:
                        connection = Connection(1, name, nameNextCell, positionCell, positionNextCell)
                        connection2 = Connection(0, nameNextCell, name, positionNextCell, positionCell)
                        connectionsList.append(connection)
                        connectionsListNextNode.append(connection2)
                        y_flag = True
                    elif typeNextCell == 8 or typeNextCell == 9 or typeNextCell == 10 and next_slider_tile_flag:
                        connection = Connection(1, name, nameNextCell, positionCell, positionNextCell)
                        connectionsList.append(connection)
                        y_flag = True
                    else:
                        connection = Connection(1, name, nameNextCell, positionCell, positionNextCell)
                        connection2 = Connection(1, nameNextCell, name, positionNextCell, positionCell)
                        connectionsList.append(connection)
                        connectionsListNextNode.append(connection2)
                        y_flag = True

            
            if y_flag is True:
                currentNodeList = self.nodesDict[name]
                if len(connectionsList) == 0:
                    pass
                else:
                    currentNodeList.append(connectionsList[0])
                
                currentNodeList = self.nodesDict[nameNextCell]
                if len(connectionsListNextNode) == 0:
                    pass
                else:
                    currentNodeList.append(connectionsListNextNode[0])
            
            connectionsList = list()
            connectionsListNextNode = list()
            
            # Checking x axis next cell
            try:
                currentColumnList = self.mapList[column + 1]
            except:
                currentColumnList = None
            
            if currentColumnList is None:
                pass
            else:
                nextCell = currentColumnList[line]
                nameNextCell = nextCell["id"]
                typeNextCell = nextCell["type"]
                positionNextCell = nextCell["position"]
                next_slider_tile_flag = False
                if typeNextCell == 9 or typeNextCell == 7 or typeNextCell == 8 or typeNextCell == 10:
                    confirmation = nextCell["config"]["is_charged"]
                    if confirmation == True:
                        next_slider_tile_flag = True
                if type == 7 or type == 8 or type == 9 or type == 10 and slider_tile_flag:
                    if type == 10:
                        if typeNextCell == 1 or typeNextCell == 3 or typeNextCell == 12  or typeNextCell == 14 or typeNextCell == 17:
                            pass
                        elif typeNextCell == 9 and next_slider_tile_flag:
                            connection = Connection(0, name, nameNextCell, positionCell, positionNextCell)
                            connection2 = Connection(0, nameNextCell, name, positionNextCell, positionCell)
                            connectionsList.append(connection)
                            connectionsListNextNode.append(connection2)
                            x_flag = True
                        elif typeNextCell == 7 or typeNextCell == 8 or typeNextCell == 10 and next_slider_tile_flag:
                            connection = Connection(0, name, nameNextCell, positionCell, positionNextCell)
                            connectionsList.append(connection)
                            x_flag = True
                        else:
                            connection = Connection(0, name, nameNextCell, positionCell, positionNextCell)
                            connection2 = Connection(1, nameNextCell, name, positionNextCell, positionCell)
                            connectionsList.append(connection)
                            connectionsListNextNode.append(connection2)
                            x_flag = True
                    else:
                        if typeNextCell == 1 or typeNextCell == 3 or typeNextCell == 12  or typeNextCell == 14 or typeNextCell == 17:
                            pass
                        elif typeNextCell == 9 and next_slider_tile_flag:
                            connection2 = Connection(0, nameNextCell, name, positionNextCell, positionCell)
                            connectionsListNextNode.append(connection2)
                            x_flag = True
                        elif typeNextCell == 7 or typeNextCell == 8 or typeNextCell == 10 and next_slider_tile_flag:
                            pass
                        else:
                            connection2 = Connection(1, nameNextCell, name, positionNextCell, positionCell)
                            connectionsListNextNode.append(connection2)
                            x_flag = True
                else:
                    if typeNextCell == 1 or typeNextCell == 3 or typeNextCell == 12  or typeNextCell == 14 or typeNextCell == 17:
                        pass
                    elif typeNextCell == 9 and next_slider_tile_flag:
                        connection = Connection(1, name, nameNextCell, positionCell, positionNextCell)
                        connection2 = Connection(0, nameNextCell, name, positionNextCell, positionCell)
                        connectionsList.append(connection)
                        connectionsListNextNode.append(connection2)
                        x_flag = True
                    elif typeNextCell == 7 or typeNextCell == 8 or typeNextCell == 10 and next_slider_tile_flag:
                        connection = Connection(1, name, nameNextCell, positionCell, positionNextCell)
                        connectionsList.append(connection)
                        x_flag = True
                    else:
                        connection = Connection(1, name, nameNextCell, positionCell, positionNextCell)
                        connection2 = Connection(1, nameNextCell, name, positionNextCell, positionCell)
                        connectionsList.append(connection)
                        connectionsListNextNode.append(connection2)
                        x_flag = True
                
            
            if x_flag is True:
                currentNodeList = self.nodesDict[name]
                if len(connectionsList) == 0:
                    pass
                else:
                    currentNodeList.append(connectionsList[0])
                
                currentNodeList = self.nodesDict[nameNextCell]
                if len(connectionsListNextNode) == 0:
                    pass
                else:
                    currentNodeList.append(connectionsListNextNode[0])
            
            # Checking if the cell is the exit
            if type == 2:
                self.idGoal.append(name)
                
        # Creating connection of bi-directional tiles
        if self.bidirectional_tile_flag is True:
            firstPosition = firstBiCell["position"]
            secondPosition = secondBiCell["position"]
            self.idFirstBiCell = firstBiCell["id"]
            self.idSecondBiCell = secondBiCell["id"]
            nodeFirstList = self.nodesDict[self.idFirstBiCell]
            nodeSecondList = self.nodesDict[self.idSecondBiCell]
            firstConnection = Connection(0, self.idFirstBiCell, self.idSecondBiCell, firstPosition, secondPosition)
            secondConnection = Connection(0, self.idSecondBiCell, self.idFirstBiCell, secondPosition, firstPosition)
            
            nodeFirstList.append(firstConnection)
            nodeSecondList.append(secondConnection)
            
            self.bidirectionalConnectionsList.append(firstConnection)
            self.bidirectionalConnectionsList.append(secondConnection)
            
        # If the player node its in a slider this node only has one connection, but we can move to other tiles, to fix this we delete all the connection of the node in where the
        # player is and use the possible moves of the jsonResponse to create connections and add him to the node
        self.nodesDict[self.idUser] = list()
        for position in jsonResponse["players"]["bearer"]["possible_moves"]:
            if position["direction"] == "stay":
                continue
            user_node = self.nodesDict[self.idUser]
            x_next = position["x"]
            y_next = position["y"]
            cell = self.mapList[x_next][y_next]
            idCell = cell["id"]
            type = cell["type"]
            if type == 0 or type == 2 or type == 4 or type == 5 or type == 6 or type == 7 or type == 8 or type == 9 or type == 10 or type == 11 or type == 13 or type == 15: 
                connection = Connection(1, self.idUser, idCell, self.userCell["position"], cell["position"])
                user_node.append(connection)
        
        # FIXME IMPORTANT: I didnt know a contructor could put blocks in death pits, if any agent is in that block when trying to access to his node 
        # will raise a index error, this is A HUGE problem, i will fix it with try except blocks because i have not better ideas
        for id in self.fullListAgents:
            try:
                self.nodesDict[id]
            except KeyError:
                if id == self.idUser:
                    self.idUser = None
                if id == self.idEnemy:
                    self.idEnemy = None
                if id == self.idRyo:
                    self.idRyo = None
                if id == self.idKix:
                    self.idKix = None
                if id == self.idLlama:
                    self.idLlama = None
                if id == self.idRipper:
                    self.idRipper = None
                if id == self.idBuzz:
                    self.idBuzz = None
                if id in self.idListAgents:
                    self.idListAgents.remove(id)
                del self.fullDictAgents[id]
    
    # Save information of the opponent, player and agents
    def saveIds(self, playersPosition, agentsPosition):
        self.idListAgents = list()
        if playersPosition["opponent"]["position"] is None:
            pass
        else:
            enemyPosition = playersPosition["opponent"]["position"]
            enemy_x = enemyPosition["x"]
            enemy_y = enemyPosition["y"]
            enemy_column = self.mapList[enemy_x]
            enemy_cell = enemy_column[enemy_y]
            self.idEnemy = enemy_cell["id"]
            self.fullListAgents.append(self.idEnemy)
            self.fullDictAgents[self.idEnemy] = 200
        
        user_x = playersPosition["bearer"]["position"]["x"]
        user_y = playersPosition["bearer"]["position"]["y"]
        user_column = self.mapList[user_x]
        self.userCell = user_column[user_y]
        self.idUser = self.userCell["id"]
        self.fullListAgents.append(self.idUser)
        self.fullDictAgents[self.idUser] = 100
        
        if len(agentsPosition) == 0:
            return None
        
        for agent in agentsPosition:
            typeAgent = agent["type"]
            agentPosition = agent["position"]
            agent_x = agentPosition["x"]
            agent_y = agentPosition["y"]
            agent_column = self.mapList[agent_x]
            agent_cell = agent_column[agent_y]
            agent_id = agent_cell["id"]
            if typeAgent == 1:
                self.idRyo = agent_id
                self.fullDictAgents[agent_id] = typeAgent
            elif typeAgent == 2:
                self.idKix = agent_id
                self.fullDictAgents[agent_id] = typeAgent
            elif typeAgent == 3:
                self.idLlama = agent_id
                self.fullDictAgents[agent_id] = typeAgent
            elif typeAgent == 4:
                self.idRipper = agent_id
                self.fullDictAgents[agent_id] = typeAgent
            elif typeAgent == 5:
                self.idBuzz = agent_id
                self.fullDictAgents[agent_id] = typeAgent
            self.fullListAgents.append(agent_id)
            self.idListAgents.append(agent_id)
            
    
    # Return the connections of the node given
    def getConnections(self, fromNode):
        listConnectionsNode = self.nodesDict[fromNode]
        
        return listConnectionsNode
        
class Connection():
    def __init__(self, cost, fromNameNode, nameNodeConnected, dictFromPosition, dictToPosition, connectionSkill=False):
        self.cost = cost
        self.fromNameNode = fromNameNode
        self.nameNodeConnected = nameNodeConnected
        self.positionFrom = dictFromPosition
        self.positionTo = dictToPosition
        self.connectionSkill = connectionSkill
        
    def __repr__(self):
        return f"#{self.fromNameNode}-->{self.nameNodeConnected}#"
        
    def getCost(self):
        return self.cost
        
    def getFromNode(self):
        return self.fromNameNode
        
    def getToNode(self):
        return self.nameNodeConnected
        
    def getCoordsTo(self):
        return self.positionTo
        
    def getCoordsFrom(self):
        return self.positionFrom
    
    def getSkillUsedConfirmation(self):
        return self.connectionSkill

class Node():
    def __init__(self, listConnections, name, nodeType=None, nodeCoords=None, charged=False):
        self.listConnections = listConnections
        self.name = name
        self.costSoFar = None
        self.pathConnections = None
        self.pathNodes = None
        self.timesReached = 0
        self.nodeType = nodeType
        self.possibleMoves = None
        self.nodeCoords = nodeCoords
        self.charged = charged
        
    def __repr__(self):
        return f"|{self.name} {self.listConnections} {self.costSoFar}|"
        
    def saveCostToReach(self, cost):
        self.costSoFar = cost
        self.timesReached = self.timesReached + 1
    
    # This function is in charge of saving in a list the connections used to get to the node, mainly to get the coords that must be sended to the game server
    def saveConnectionUsed(self, connectionObject):
        if self.pathConnections is None:
            self.pathConnections = list()
        
        if connectionObject is None:
            pass
        elif type(connectionObject) is list:
            for connection in connectionObject:
                if connection is None:
                    continue
                self.pathConnections.append(connection)
        else:
            self.pathConnections.append(connectionObject)
        
    # Special function used for saving the possible moves(connections) of Ryo
    def savePossibleMoves(self, idListAgents):
        self.possibleMoves = copy.deepcopy(self.listConnections)
        for connection in self.possibleMoves:
            idEndNode = connection.getToNode()
            if idEndNode in idListAgents:
                self.possibleMoves.remove(connection)
    
    # This just creates a list with the nodes that where used to reach the node, take into account that this may fail if the pathConnections was not created this is 
    # just the case for the player node but i am not sure
    def createListOfNodes(self):
        self.pathNodes = list()
        firstIter_Flag = True
        for connection in self.pathConnections:
            if firstIter_Flag:
                fromNode = connection.getFromNode()
                self.pathNodes.append(fromNode)
            
            toNode = connection.getToNode()
            self.pathNodes.append(toNode)
                
            firstIter_Flag = False
        
        return self.pathNodes
    
    def getType(self):
        return self.nodeType
        
    def deletePath(self):
        self.pathConnections = None
        self.costSoFar = None
        self.timesReached = 0
    
    def getPathConnections(self):
        return self.pathConnections
        
    def getFirstConnection(self):
        # IMPROVE: If there is no exit node and we are close to ryo in one of his adyacent nodes dijkstra will considered the place we are is the less expensive path
        # and when calling this function will return a None object, this will also happen if we are trapped so to prevent this we use the nodeCoords to create a  
        # connection that points to the node, connections returned by this function should be double checked, and only used outside this code
        try:
            self.pathConnections[0]
        except TypeError:
            connection = Connection(1, -1, -1, self.nodeCoords, self.nodeCoords)
            self.pathConnections = list()
            self.pathConnections.append(connection)
            
        return self.pathConnections[0]
        
class infinityDectector():
    def __init__(self):
        self.Count = 0
        
    def CountIter(self):
        self.Count = self.Count + 1
        if self.Count > 100:
            raise ValueError("INFINITY LOOP DETECTED!")

# Converts the dictionary of the graph object (a dictionary of dictionaries) to a dictionary of nodes and assings them his type and coords
def converter(graphObject):
    trueNodesDict = dict()
    nodesDict = graphObject.nodesDict
    mapDict = graphObject.mapDict
    for (k, v) in nodesDict.items():
        cell = mapDict[k]
        nodeType = cell["type"]
        coordsNode = cell["position"]
        charged = False
        if nodeType == 7 or nodeType == 8 or nodeType == 9 or nodeType == 10:
            charged = cell["config"]["is_charged"]
            
        trueNodesDict[k] = Node(v, k, nodeType, coordsNode, charged)
    
    return trueNodesDict

# function to restore path values of a nodesDict object, used in dijkstra function
def restoreValues(nodesDict):
    for (id, node) in nodesDict.items():
        node.deletePath()

# Creates a map, nodesDict must be the one created from the coverter function (the node type is necessary for this function), the fullDictAgents is from the graphObject
def getMap(nodesDict, mapList, graphObject):
    fullDictAgents = graphObject.fullDictAgents
    mapStr = str()
    
    column = mapList[0]
    lengColumn = len(column)
    
    totalCells = lengColumn * lengColumn
    
    Count = 1
    order = sorted(nodesDict)
    for n in range(totalCells):
        confirmation_flag = True
        for num in order:
            if n == num:
                node = nodesDict[num]
                nodeType = node.getType()
                character = compareIds(num, fullDictAgents, nodesDict)
                mapStr = f"{mapStr}{character}"
                
                confirmation = Count%lengColumn
                if confirmation == 0:
                    mapStr = f"{mapStr}\n"
                
                confirmation_flag = False
        if confirmation_flag:
            mapStr = f"{mapStr} "
            
            confirmation = Count%lengColumn
            if confirmation == 0:
                mapStr = f"{mapStr}\n"
            
        Count = Count + 1
    # Putting the map into the correct orientation
    finalStr = str()
    mapStr = mapStr.rstrip("\n")
    mapSplited = mapStr.split("\n")
    lengLines = len(mapSplited[0])
    CountIter = 0
    # There is the possibility than this loop never ends if its modified incorrectly, i wouldn't touch this if its not necessary
    while CountIter >= (int(f"-{len(mapSplited)}")+1):
        Count = 0
        if Count == CountIter:
            pass
        else:
            Count = CountIter
            
        for line in mapSplited:
            for letter in line:
                confirmation = Count%lengLines
                Count = Count + 1
                if confirmation == 0:
                    finalStr = f"{finalStr}{letter} "
        
        finalStr = f"{finalStr}\n"
        CountIter = CountIter - 1
        
    return finalStr

# This function was created for the getMap function to reduce indentation
def compareIds(numVerification, fullDictAgents, nodesDict):
    character = None
    for (id, type) in fullDictAgents.items():
        if id == numVerification:
            if type == 1:
                character = "R"
            elif type == 2:
                character = "K"
            elif type == 3:
                character = "L"
            elif type == 4:
                character = "!"
            elif type == 5:
                character = "B"
            elif type == 100:
                character = "P"
            elif type == 200:
                character = "E"
    
    if character is None:
        node = nodesDict[numVerification]
        nodeType = node.getType()
        if nodeType == 2:
            character = "#"
        elif nodeType == 7:
            character = "^"
        elif nodeType == 8:
            character = "~"
        elif nodeType == 9:
            character = "<"
        elif nodeType == 10:
            character = ">"
        elif nodeType == 11:
            character = "0"
        elif nodeType == 13:
            character = "$"
        elif nodeType == 14:
            character = "*"
        elif nodeType == 15:
            character = "'"
        else:
            character = "+"
        
    
    return character

# Same as getMap() but it takes only the jsonResponse, creates all the info for the getMap function
def createMap(jsonResponse):
    graphObject = Graph(jsonResponse)
    mapList = graphObject.mapList
    nodesDict = converter(graphObject)
    mapToReturn = getMap(nodesDict, mapList, graphObject)
    return mapToReturn

# The heart function of the bot, in charge of finding the paths with less cost to goal nodes
def dijkstra(nodesDict, idUser, idsGoal):
    idsGoalNodes = list()
    if type(idsGoal) is not list:
        idsGoalNodes.append(idsGoal)
    else:
        idsGoalNodes = idsGoal
        
    goalNodes = list()
    for id in idsGoalNodes:
        goalNodes.append(nodesDict[id])
    
    #Restoring path values in case the nodesDict object has already been proccessed by dijkstra before
    restoreValues(nodesDict)
    
    openList = list()
    closedList = list()
    
    nodePlayer = nodesDict[idUser]
    nodePlayer.saveCostToReach(0)
    openList.append(nodePlayer)
    
    while len(openList) > 0:
        for node in openList:
            listConnections = node.listConnections
            nodeCost = node.costSoFar
            nodeListPath = node.pathConnections
            for connection in listConnections:
                idNextNode = connection.getToNode()
                nextNode = nodesDict[idNextNode]
                nextNodeCost = nextNode.costSoFar 
            
                costSoFar = connection.getCost() + nodeCost
                if nextNodeCost is None:
                    nextNode.saveCostToReach(costSoFar)
                    nextNode.saveConnectionUsed(nodeListPath)
                    nextNode.saveConnectionUsed(connection)
                    openList.append(nextNode)
                else:
                    if costSoFar >= nextNodeCost:
                        pass
                    elif costSoFar <  nextNodeCost:
                        nextNode.pathConnections = None
                        if nextNode in closedList:
                            closedList.remove(nextNode)
                            openList.append(nextNode)
                            nextNode.saveCostToReach(costSoFar)
                            nextNode.saveConnectionUsed(nodeListPath)
                            nextNode.saveConnectionUsed(connection)
                        else:
                            nextNode.saveCostToReach(costSoFar)
                            nextNode.saveConnectionUsed(nodeListPath)
                            nextNode.saveConnectionUsed(connection)
                        
            openList.remove(node)
            closedList.append(node)
    
    endList = list()
    for node in goalNodes:
        if node in closedList:
            endList.append(node)
    
    winnerNode = None
    currentCost = None
    for node in endList:
        nodeCost = node.costSoFar
        if currentCost is None:
            currentCost = nodeCost
            winnerNode = node
        else:
            if nodeCost < currentCost:
                currentCost = nodeCost
                winnerNode = node
        
    if len(endList) == 0 or winnerNode is None:
        # IMPROVE: If the goal nodes are unreachable it means we are sorrounded by obstacles type 17, 14, 1 or 3 if that happens we can only calculate a node far from the enemy if we are 
        # trapped with him, but i dont have good ideas of how do it, i will choose a random node until the obstacles type 17 dissapear or the match ends
        winnerNode = random.choice(closedList)
        return winnerNode
    else:
        return winnerNode
    

# NOTE: This function is in charge of, as his name implies, creating a ideal path depending of the operator Skill, i am using a operator with swap skill, if you are using other
# operator add your code here and delete or "sleep" with conditionals the code that use the swap skill
def strategyPath(jsonResponse):
    # Object to prevent and stop infinite loops, use in while loops
    x = infinityDectector()
    graphObject = Graph(jsonResponse)
    mapList = graphObject.mapList
    nodesDict = converter(graphObject)
    
    idUser = graphObject.idUser
    idGoal = graphObject.idGoal
    idEnemy = graphObject.idEnemy
    idRipper = graphObject.idRipper
    idBuzz = graphObject.idBuzz
    idRyo = graphObject.idRyo
    
    idListAgents = graphObject.idListAgents
    
    fullListAgents = list()
    almostFullListAgents = list()
    for id in idListAgents:
        almostFullListAgents.append(id)
        fullListAgents.append(id)
    
    almostFullListAgents.append(idEnemy)
    fullListAgents.append(idUser)
    
    # Saving the possible moves (copy of his listConnections) of Ryo and Ripper
    ryoNode = nodesDict[idRyo]
    ryoNode.savePossibleMoves(almostFullListAgents)
    
    isRipperTime_flag = False
    if idRipper is None:
        pass
    else:
        isRipperTime_flag = True
        ripperNode = nodesDict[idRipper]
        ripperNode.savePossibleMoves(fullListAgents)
    
    # NOTE: This code deletes the connections of the nodes in wich the enemy player and agents are, since this is necessary to create a perfect path i dont see a reason
    # to not execute this each call of the function unless you are using a operator with the swap skill, in that case nothing is deleted since each agent cell
    # if possible could be a potential path

    skillStatus = graphObject.skillStatus
    skill = graphObject.skill        
    swapSkill_flag = False
    if skill.lower() == "swap" and skillStatus == 1:
        swapSkill_flag = True
        swapSkill_flag = False
    else:
        for idNode in almostFullListAgents:
            agentNode = nodesDict[idNode]
            agentNode.listConnections = list()
        deleteConnectionsAgentsNodes(nodesDict, almostFullListAgents)
    
    # Swap Skill code
    # 1st : There is two ways of wining with a agent with only swap skill, trapping Ryo or reaching the goal (exit), to decide wich path use, first we use the list that we
    # reciently made ( ryoNode.savePossibleMoves(almostFullListAgents) ) to check the possible moves of ryo if its 1 it means we can considered as a goal node if it doesnt we 
    # prioritize the goal node in case there is no goal node then the possible moves/the end nodes of the connections of Ryo should be considered as goal nodes 
    
    ryoConnections = ryoNode.possibleMoves
    listIdsGoals = list()
    ryoIdsGoals = list()
    if len(idGoal) == 0:
        for connection in ryoConnections:
            idTempGoal = connection.getToNode()
            listIdsGoals.append(idTempGoal)
            ryoIdsGoals.append(idTempGoal)
    else:
        nodeGoal = dijkstra(nodesDict, idUser, idGoal)
        goalName = nodeGoal.name
        if goalName in idGoal:
            if len(ryoConnections) == 1:
                connection = ryoConnections[0]
                secondGoalNode = connection.getToNode()
                # Checking that the connection doesnt point to a charged slider and if it does it must point to the ryo node otherwise should not be taken into account
                adyacent_node = nodesDict[secondGoalNode]
                nodeType = adyacent_node.nodeType
                charged = adyacent_node.charged
                if nodeType == 7 or nodeType == 8 or nodeType == 9 or nodeType == 10 and charged:
                    # FIXME: In case the slider points to a obstacle or agent it can be considered a nodeGoal since it we wont move if we go there, most of the times,
                    # if it points to a death pit/mine well, we die
                    # This only works if the connections of the nodes where the agents are were deleted 
                    if len(adyacent_node.listConnections) == 0 and swapSkill_flag is False:
                        listIdsGoals.append(secondGoalNode)
                        ryoIdsGoals.append(secondGoalNode)
                    # if it has a connection it means that if we go there we will get pushed
                    elif len(adyacent_node.listConnections) > 0 and swapSkill_flag is False:
                        pass
                    # If the connections weren't deleted, then it has two cases, it points to a obstacle/pit/mine so it has no connections, so we go there taking the risk
                    # that we may end dying, or wining
                    elif len(adyacent_node.listConnections) == 0 and swapSkill_flag is True:
                        listIdsGoals.append(secondGoalNode)
                        ryoIdsGoals.append(secondGoalNode)
                    # The second case is that the connection may be pointing to ryo or other node we check that and pass if it not points to ryo
                    elif len(adyacent_node.listConnections) > 0 and swapSkill_flag is True:
                        connection = adyacent_node.listConnections[0]
                        if idRyo == connection.getToNode():
                            listIdsGoals.append(secondGoalNode)
                            ryoIdsGoals.append(secondGoalNode)
                        else:
                            pass
                else:
                    listIdsGoals.append(secondGoalNode)
                    ryoIdsGoals.append(secondGoalNode)
            for id in idGoal:
                listIdsGoals.append(id)
        else:
            for connection in ryoConnections:
                idTempGoal = connection.getToNode()
                listIdsGoals.append(idTempGoal)
                ryoIdsGoals.append(idTempGoal)
            for id in idGoal:
                listIdsGoals.append(id)
                
            
    # 2nd : The first of the swap skill could honestly be used always but i am leaving there for now since to other operators its possible to win killing a enemy too.
    # To use the swap skill we should adapt the nodes for this, here we can use the "possible targets" of the jsonResponse to create a connection between the user 
    # node and the target nodes
    
    listNodesToConnect = jsonResponse["players"]["bearer"]["skills"][0]["possible_targets"]
    targets_flag = False
    if len(listNodesToConnect) > 0:
        targets_flag = True
    
    if swapSkill_flag is True and targets_flag:
        for coordsNodeToConnect in listNodesToConnect:
            x_NodeToConnect = coordsNodeToConnect["x"]
            y_NodeToConnect = coordsNodeToConnect["y"]
            agentColumn = mapList[x_NodeToConnect]
            agentCell = agentColumn[y_NodeToConnect]
            idAgentCell = agentCell["id"]
            # FIXME IMPORTANT: Second Fix of the error cause if a constructor operator put a block in a pit and any agent node goes to it
            try:
                agent_node = nodesDict[idAgentCell]
            except KeyError:
                continue
            agentConnectionsList = agent_node.listConnections
            # This is just in case the listConnections is empty (the target node has no possible moves), i dont see scenaries where that could happen but hey, it doesnt hurt 
            if len(agentConnectionsList) == 0 or agentConnectionsList is None:
                pass
            else:
                connection = agentConnectionsList[0]
                coordsAgentNode = connection.positionFrom
                coordsUserNode = jsonResponse["players"]["bearer"]["position"]
                skillConnection = Connection(0, idUser, idAgentCell, coordsUserNode, coordsAgentNode, True)
                userNode = nodesDict[idUser]
                userNode.listConnections.append(skillConnection)
    
    # Third part Of Swap Skill Code
    
    # 3rd  Ripper Code : Ripper is instakill so getting close is not good, normaly with other operators the solution cloud be just deleting the connectionsList of the adyacent
    # nodes of the Ripper but with swap its possible to bypassing him, but even with the swap skill there is the possibility of falling in one of his adyacent nodes by example
    # if he is in a corner, the solution, we check only the first connection of the pathConnections in the nodeGoal if the connection points to a adyacent Ripper Node we delete 
    # the connectionsList of that node and recalculate a new path, i call it "One step to death" strategy, its not too efective since the amount of turns of him are 3, i think,
    # but deleting the connections of too many nodes can cause to not be able of create a decent path to the goal

    # Looping the verification to make sure the first connection of the new path doesnt points to other Ripper node
    alreadyCalculated_flag = False
    noDanger_flag = True
    while noDanger_flag:
        infinityDectector.CountIter(x)
        nextToDead_flag = False
        if swapSkill_flag is True and isRipperTime_flag is True:
            # Execution of the dijkstra algorithm
            nodeGoal = dijkstra(nodesDict, idUser, listIdsGoals)
            
            alreadyCalculated_flag = True
            ripperPossibleMoves = ripperNode.possibleMoves
            goalPathConnections = nodeGoal.pathConnections
            # In case the goal node is the player node
            if goalPathConnections is None:
                break
            else:
                firstConnection = goalPathConnections[0]
                idNextNode = firstConnection.getToNode()
                for connection in ripperPossibleMoves:
                    idAdyacentNodeRipper = connection.getToNode()
                    if idNextNode == idAdyacentNodeRipper:
                        nextToDead_flag = True
        elif isRipperTime_flag is True:
            ripperPossibleMoves = ripperNode.possibleMoves
            for connection in ripperPossibleMoves:
                idAdyacentNode =connection.getToNode()
                adyacentNode = nodesDict[idAdyacentNode]
                adyacentNode.listConnections = list()
            
        if nextToDead_flag:
            adyacentNode = nodesDict[idNextNode]
            adyacentNode.listConnections = list()
        else:
            if alreadyCalculated_flag is False:
                nodeGoal = dijkstra(nodesDict, idUser, listIdsGoals)
            else:
                pass
            break
    
    # 4th Buzz swap code: If Ryo is sorrounded by Buzz and we are close its highly possible that the path uses Buzz to get close to Ryo wich can cause to him teleporting or 
    # losing a opportunity to win so to fix this we check that the first connection of the path points to the buzz node and the end of connection or goal node of the
    # path its not a adyacent Ryo Node, if the two are True that means is going to swap to buzz to get to a adyacent Ryo node.
    # I notice its utilize swap in Ryo to get close to one of his adyacent node, so the fix is the same as buzz 
    if swapSkill_flag:
        pathConnections = nodeGoal.pathConnections
        if pathConnections is None:
            pass
        else:
            # Looping in case the first path uses ryo and the second uses buzz
            while True:
                infinityDectector.CountIter(x)
                nodeGoal = dijkstra(nodesDict, idUser, listIdsGoals)
                pathConnections = nodeGoal.pathConnections
                checking_firstFlag = False
                checking_secondFlag = False
                firstConnection = pathConnections[0]
                idNextNode = firstConnection.getToNode()
                pathReversed = reversed(pathConnections)
                pathReversed = list(pathReversed)
                lastConnection = pathReversed[0]
                idLastNode = lastConnection.getToNode()
                if idBuzz == idNextNode and idLastNode in ryoIdsGoals:
                    userNode = nodesDict[idUser]
                    tempList = list()
                    for connection in userNode.listConnections:
                        confirmation = connection.getSkillUsedConfirmation()
                        if confirmation is True:
                            tempList.append(connection)
                    for skillConnection in tempList:
                        if skillConnection.getToNode() == idBuzz:
                            userNode.listConnections.remove(connection)
                    nodeGoal = dijkstra(nodesDict, idUser, listIdsGoals)
                else:
                    checking_firstFlag = True
                    
                if idRyo == idNextNode and idLastNode in ryoIdsGoals:
                    userNode = nodesDict[idUser]
                    # I never knew that removing a item from a list in a loop, if that list is used for the loop, it ends up executing less times, not iterating
                    # all the items of the list, thats why first must be appended to a external list and after execute the remove function
                    tempList = list()
                    for connection in userNode.listConnections:
                        confirmation = connection.getSkillUsedConfirmation()
                        if confirmation is True:
                            tempList.append(connection)
                    for skillConnection in tempList:
                        if skillConnection.getToNode() == idRyo:
                            userNode.listConnections.remove(connection)
                    nodeGoal = dijkstra(nodesDict, idUser, listIdsGoals)
                else:
                    checking_secondFlag = True
                
                if checking_firstFlag is True and checking_secondFlag is True:
                    break
            
    # This code checks if the nodeGoal path used the bidirectional tile connection or not, in case it did but as a normal node the connections of the bidirectional 
    # tiles must be deleted, so it doesnt take it as a valid node and re-calculate a new and valid path, this is the only solution i could think of for now
    if graphObject.bidirectional_tile_flag:
        # If the goal node is the player node it will fail so we verify that
        try:
            goalNodesList = nodeGoal.createListOfNodes()
        except TypeError:
            goalNodesList = list()
            
        idFirstBiCell = graphObject.idFirstBiCell
        idSecondBiCell = graphObject.idSecondBiCell
    
        usedBiNode_flag = False
        for idNode in goalNodesList:
            if idNode == idFirstBiCell or idNode == idSecondBiCell:
                usedBiNode_flag = True
    
        nodesMap = getMap(nodesDict, mapList, graphObject)
    
        listConnectionsBidirectional = graphObject.bidirectionalConnectionsList
    
        usedBidirectionalConnection_flag = False
        if usedBiNode_flag is True:
            for goalConnection in nodeGoal.pathConnections:
                if goalConnection in listConnectionsBidirectional:
                    usedBidirectionalConnection_flag = True
    
        if usedBiNode_flag is True and usedBidirectionalConnection_flag is False:
            firstBiNode = nodesDict[idFirstBiCell]
            secondBiNode = nodesDict[idSecondBiCell]
        
            firstBiNode.listConnections = list()
            secondBiNode.listConnections = list()
        
            nodeGoal = dijkstra(nodesDict, idUser, listIdsGoals)
        
            nodesMap = getMap(nodesDict, mapList, graphObject)
        
    return nodeGoal
        
def deleteConnectionsAgentsNodes(nodesDict, almostFullListAgents):
    for id in almostFullListAgents:
        for (name, node) in nodesDict.items():
            for connection in node.listConnections:
                connectionPointsTo = connection.getToNode()
                if id == connectionPointsTo:
                    node.listConnections.remove(connection)