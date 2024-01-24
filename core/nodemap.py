# Version 2.0 
# The first version of this code was made with the intention of not spend too much memory, the result was an awfull code because there was a lot of errors, 
# this version creates a lot of classes and uses a lot of loops sometimes so its probably going to use much memory, the advantajes is better readability, 
# defines (hopefully permanently) the basic structure and best way of create the graph, nodes and connections objects to be easy modifiable in case is needed
import random
import copy


class Connection():
    def __init__(self, cellFrom: dict, cellTo: dict, cost=1, usedSkill=False, idSkill=None, ban=False):
    # INFO: After separating the types of connections (attack, movement...), usedSkill and idSkill variables are not longer need it, but can maybe be still
    # usefull in some cases to check if a connection is a skill connection instead of making reference to his class?
        self.nodeFrom = None
        self.nodeTo = None
        self.fromNode = cellFrom["id"]
        self.typeFromNode = cellFrom["type"]
        self.positionFrom = cellFrom["position"]
        self.toNode = cellTo["id"]
        self.typeToNode = cellTo["type"]
        self.positionTo = cellTo["position"]
        self.cost = cost
        self.usedSkill = usedSkill
        self.idSkill = idSkill
        self.damage = None
        self.ban = ban
    
    def __repr__(self):
        baseStr = f"#{self.fromNode}-{self.typeFromNode}--{self.cost}--{self.typeToNode}->{self.toNode}"
        if self.usedSkill:
            baseStr = f"{baseStr} Skill Used"
        if self.ban:
            baseStr = f"{baseStr} BANNED"
        baseStr = f"{baseStr}#"
        
        return baseStr
        
    def setCost(self, cost: int) -> None:
        self.cost = cost
    
    def setBan(self, ban: bool) -> None:
        self.ban = ban
    
    def setDamage(self, damage: int) -> None:
        self.damage = damage
    
    @classmethod
    def initWithNodes(cls, nodeFrom, nodeTo, cost=1, usedSkill=False, idSkill=None, ban=False):
        cellFrom = nodeFrom.cell
        cellTo = nodeTo.cell
        clsObj = cls(cellFrom, cellTo, cost, usedSkill, idSkill, ban)
        clsObj.nodeFrom = nodeFrom
        clsObj.nodeTo = nodeTo
        
        return clsObj


class Node():
    def __init__(self, cell: dict):
        self.cell = cell
        # FIX: I just noticed this name conflict, i will fix it, some day
        self.id = cell["id"]
        self.typeNode = cell["type"]
        self.position = cell["position"]
        self.config = cell["config"]
        self.nameNode = cell["name"]
        self.listConnections = list()
        self.listAgentConnections = list()
        self.dictIdNearNodes = dict()
        self.typeAgentIn = None
        self.totalLife = None
        
        # Each Node has access to the graph, making easy the access to info about all the nodes
        self.dictGraphNodes = None
        
        # Variables destined to use in the dijkstra algorithm
        self.costToReach = None
        self.pathConnections = list()
        
        
    def __repr__(self):
        return f"Node Id:{self.id} Type:{self.typeNode} listConnections:{self.listConnections}"
        
    def saveAdyacentConnections(self, map: list) -> None:
        x_value = self.position["x"]
        y_value = self.position["y"]
        dictIdNearNodes = dict()
        listCells = list()
        try:
            cell_right = map[x_value + 1][y_value]
            listCells.append(cell_right)
            dictIdNearNodes["right"] = cell_right["id"]
        except IndexError:
            dictIdNearNodes["right"] = None
        try:
            cell_down = map[x_value][y_value + 1]
            listCells.append(cell_down)
            dictIdNearNodes["down"] = cell_down["id"]
        except IndexError:
            dictIdNearNodes["down"] = None
        if x_value > 0:
            cell_left = map[x_value - 1][y_value]
            listCells.append(cell_left)
            dictIdNearNodes["left"] = cell_left["id"]
        else:
            dictIdNearNodes["left"] = None
        if y_value > 0:
            cell_up = map[x_value][y_value - 1]
            listCells.append(cell_up)
            dictIdNearNodes["up"] = cell_up["id"]
        else:
            dictIdNearNodes["up"] = None
        
        self.dictIdNearNodes = dictIdNearNodes
        for cell in listCells:
            connection = Connection(self.cell, cell)
            self.listConnections.append(connection)
    
    def deleteInvalidConnections(self, listIds: list) -> None:
        tmpList = list()
        for connection in self.listConnections:
            if connection.typeToNode in listIds:
                tmpList.append(connection)
        
        for connection in tmpList:
            self.listConnections.remove(connection)
        
    def deleteConnections(self) -> None:
        self.listConnections = list()
    
    def addConnection(self, connection: Connection) -> None:
        self.listConnections.append(connection)
        
    def setTypeAgentIn(self, typeAgent: int) -> None:
        self.typeAgentIn = typeAgent
    
    def setCostToReach(self, cost: int) -> None:
        self.costToReach = cost
    
    def savePathConnections(self, connections: list):
        for connection in connections:
            self.pathConnections.append(connection)
    
    def deletePathConnections(self):
        self.pathConnections = list()
        self.costToReach = None
    
    def loadUniqueConfig(self):
        pass
    
# Complex Connections
# These connections can be created with nodes, as his name implies "nodeFrom", but it can also be created with cells, like a normal connnection but depending of
# the class of connection it could throw an error if depends of the data nodes (like AttackSkill)

class SkillCellConnection(Connection):
    def __init__(self, nodeFrom, nodeTo, cost=1, usedSkill=False, idSkill=None, ban=False):
        super().__init__(nodeFrom, nodeTo, cost, usedSkill, idSkill, ban)

class BidirectionalConnection(SkillCellConnection):
    def __init__(self, nodeFrom, nodeTo, cost=1, usedSkill=False, idSkill=None, ban=False):
        super().__init__(nodeFrom, nodeTo, cost, usedSkill, idSkill, ban)


class SkillConnection(Connection):
    def __init__(self, nodeFrom, nodeTo, infoSkill: dict, cost=1, usedSkill=True, idSkill=None, ban=False):
        if type(nodeFrom) is dict and type(nodeTo) is dict:
            super().__init__(nodeFrom, nodeTo, cost, usedSkill, idSkill, ban)
        elif isinstance(nodeFrom, Node) and isinstance(nodeTo, Node):
            super().__init__(nodeFrom.cell, nodeTo.cell, cost, usedSkill, idSkill, ban)
            self.nodeFrom = nodeFrom
            self.nodeTo = nodeTo
        else:
            raise ValueError("Type of Nodes/Cells is wrong, please check those values")
        
        self.infoSkill = infoSkill
        self.idSkill = infoSkill["id"]
        self.nameSkill = infoSkill["name"]
        self.castCost = infoSkill["cost"]


class MovementSkill(SkillConnection):
    def __init__(self, nodeFrom, nodeTo, infoSkill: dict, cost=1, usedSkill=True, idSkill=None, ban=False):
        super().__init__(nodeFrom, nodeTo, infoSkill, cost, usedSkill, idSkill, ban)


class AttackSKill(SkillConnection):
    def __init__(self, nodeFrom, nodeTo, infoSkill: dict, cost=1, usedSkill=True, idSkill=None, ban=False):
        super().__init__(nodeFrom, nodeTo, infoSkill, cost, usedSkill, idSkill, ban)
        self.damage = self.infoSkill["damage"]
        self.againstAgent = False
        self.againstTrap = False
        self.againstSentry = False
        self.killConfirmation = False
        
        if type(self.nodeTo) is AgentNode:
            self.againstAgent = True
        elif type(self.nodeTo) is TrapNode:
            self.againstTrap = True
        elif type(self.nodeTo) is SentryNode:
            self.againstSentry = True
        if self.againstAgent and self.damage >= self.nodeTo.totalLife:
            self.killConfirmation = True
    
    def __repr__(self):
        baseStr = f"#{self.fromNode}-{self.nodeFrom.nameNode}--{self.damage}--{self.nodeTo.nameNode}->{self.toNode} SKILL: {self.nameSkill}"
        
        if self.killConfirmation is True:
            baseStr = f"{baseStr} KILL!!"
        if self.ban:
            baseStr = f"{baseStr} BANNED"
        baseStr = f"{baseStr}#"
        
        return baseStr

# Complex Nodes

class ChildNode(Node):
    def __init__(self, cell: dict):
        super().__init__(cell)
        

class SliderNode(ChildNode):
    def __init__(self, cell: dict):
        super().__init__(cell)
        self.isCharged = self.config["is_charged"]
        self.toNode = None
    
    def saveAdyacentConnections(self, map: list) -> None:
        super().saveAdyacentConnections(map)
        
        for connection in self.listConnections:
            connection.setCost(0)
            self.toNode = connection.toNode
    
    def deleteInvalidConnections(self, listIds: list) -> None:
        super().deleteInvalidConnections(listIds)
        # Info: We asume that the listIds has the id of the nodes that are inamovible, if thats not the case in the future, the code to prevent 
        # deleting the connection (uniqueSliderConn) must be changed
        charged = self.config["is_charged"]
            
        dictSliderTypes = [{"type": 7, "direction": "up"}, {"type": 8, "direction": "down"}, {"type": 9, "direction": "left"}, {"type": 10, "direction": "right"}]
        deleteConn_flag = True
        tmpList = list()
        uniqueSliderConn = None
        if charged is False:
            pass
        else:
            for dictSlider in dictSliderTypes:
                if self.typeNode == dictSlider["type"] and self.dictIdNearNodes[dictSlider["direction"]] is not None:
                    for connection in self.listConnections:
                        if connection.toNode != self.dictIdNearNodes[dictSlider["direction"]]:
                            tmpList.append(connection)
                        else:
                            uniqueSliderConn = connection
        
        if uniqueSliderConn:
            nextNodeType = self.dictGraphNodes[uniqueSliderConn.toNode].typeNode
            nextNodeAgent = self.dictGraphNodes[uniqueSliderConn.toNode].typeAgentIn
            if nextNodeAgent is not None:
                deleteConn_flag = False
            elif nextNodeType in listIds:
                deleteConn_flag = False
        
        if deleteConn_flag:
            for connection in tmpList:
                self.listConnections.remove(connection)
        
    
class BidirectionalNode(ChildNode):
    def __init__(self, cell: dict):
        super().__init__(cell)
        self.isCharged = self.config["is_charged"]
    
    def loadUniqueConfig(self):
        if self.isCharged is False:
            return None
        tmpList = [connection for connection in self.listConnections if type(connection) is not BidirectionalConnection]
        for connection in tmpList:
            self.listConnections.remove(connection)
        
        self.isCharged = False
        
class PitNode(ChildNode):
    def __init__(self, cell: dict):
        super().__init__(cell)

class TrapNode(ChildNode):
    def __init__(self, cell: dict):
        super().__init__(cell)

class SentryNode(ChildNode):
    def __init__(self, cell: dict):
        super().__init__(cell)

class ObstacleNode(ChildNode):
    def __init__(self, cell: dict):
        super().__init__(cell)

class IceNode(ChildNode):
    def __init__(self, cell: dict):
        super().__init__(cell)
    
    def saveAdyacentConnections(self, map: list) -> None:
        super().saveAdyacentConnections(map)
        
        for connection in self.listConnections:
            connection.setCost(0)
            self.toNode = connection.toNode

class PlayerNode(ChildNode):
    def __init__(self, cell: dict):
        super().__init__(cell)
        self.totalLife = None
    
    def savePossibleMoves(self, possibleMoves: list, map: list):
        self.deleteConnections()
        for move in possibleMoves:
            nextCell = getCell(move, map)
            
            connection = Connection(self.cell, nextCell) 
            self.addConnection(connection)
            
    def playerNodeIsGoal(self):
        for connection in self.listConnections:
            if connection.fromNode == connection.toNode:
                self.pathConnections.append(connection)
        if len(self.pathConnections) > 1 or len(self.pathConnections) == 0:
            print("WARNING: playerNodeIsGoal function has found two connections or nothing!")
            
    def saveStats(self, dictStats: dict):
        self.nameNode = dictStats["name"]
        self.armor = dictStats["stats"]["armor"]
        self.hitpoints = dictStats["stats"]["hitpoints"]
        
        self.totalLife = self.armor + self.hitpoints
        
class EnemyNode(ChildNode):
    def __init__(self, cell: dict):
        super().__init__(cell)
        self.listConnectionsCopy = list()
        self.totalLife = None
        
    def copyListConnections(self):
        self.listConnectionsCopy = copy.deepcopy(self.listConnections)
    
    def saveStats(self, dictStats: dict):
        self.nameNode = dictStats["name"]
        self.armor = dictStats["stats"]["armor"]
        self.hitpoints = dictStats["stats"]["hitpoints"]
        
        self.totalLife = self.armor + self.hitpoints

class AgentNode(ChildNode):
    def __init__(self, cell: dict):
        super().__init__(cell)
        self.listConnectionsCopy = list()
        self.totalLife = None
        
    def copyListConnections(self):
        self.listConnectionsCopy = copy.deepcopy(self.listConnections)
    
    def saveStats(self, dictStats: dict):
        self.nameNode = dictStats["name"]
        self.armor = dictStats["stats"]["armor"]
        self.hitpoints = dictStats["stats"]["hitpoints"]
        self.typeAgentIn = dictStats["type"]
        
        self.totalLife = self.armor + self.hitpoints

# Class used in some while loops that are supossed to loop only a few times
class InfinityDetector():
    def __init__(self):
        self.Count = 0
        
    def CountIter(self):
        self.Count = self.Count + 1
        if self.Count > 100:
            raise ValueError("INFINITY LOOP DETECTED!")

class Graph():
    def __init__(self, jsonResponse):
        self.state = jsonResponse["state"]
        self.players = jsonResponse["players"]
        self.specialAgents = jsonResponse["special_agents"]
        self.map = jsonResponse["map"]
        self.verdict = jsonResponse["verdict"]
        
        # NOTE: This cells are supposse to be always non None, and the rest of the code asumes this because if not then its not an game in course, if you get and error because
        # these (user, player and ryo) are None check that you are passing a jsonResponse from a game in course
        self.userCell = None
        self.enemyCell = None
        self.ryoCell = None
        self.userNode = None
        self.enemyNode = None
        self.ryoNode = None
        
        self.kixCell = None
        self.llamaCell = None
        self.ripperCell = None
        self.buzzCell = None
        self.kixNode = None
        self.llamaNode = None
        self.ripperNode = None
        self.buzzNode = None
        
        self.listIdAgentsSorrounding = list()
        self.ryoTrapped_flag = False
        self.ryoIdGoal = None
        
        self.listIdAgents = list()
        self.dictAgentsCells = dict()
        
        # Saving cells of player and agents
        self.saveCells()
        
        # Flag to confirme the status of the bidirectional tiles
        self.bidirectionalTileActive_flag = False
        
        self.listIdBidirectionals = list()
        self.listConnectionsBidirectionals = list()
        self.listIdGoals = list()
        self.dictNodes = dict()
        self.dictNodesPure = dict()
        dictNodes = dict()
        
        listCells = list()
        for column in self.map:
            for cell in column:
                listCells.append(cell)

        # INFO: If the game is updated with new cell types, the code will handle them like invalid nodes, several Warning messages will alert about this,
        # so report it to me or if you understand the code a little you can create a new class for it
        # 12: Death Pit  13: Zap Trap  14: Mine  15: Bobby trap  16: Sentry Turret  17: Lesser Obstacle  18: Ice Cell
        listIdKnownNodes = {idNode for idNode in range(19)}
        # Invalid nodes are nodes that are not possible to go("enter")
        listIdInvalidNodes = {1, 3, 16, 17}
        listTypesSlider = {7, 8, 9, 10}
        idBidirectional = 11
        idDeathPit = 12
        listIdTraps = {13, 14, 15}
        idSentryTurret = 16
        idLesserObstacle = 17
        idIce = 18
        for cell in listCells:
            # No matter the type of the cell its added to the dictNodes, the key is the unique id and the value is a nade object with a list of  
            # connections that could be empty or with the connections if its a valid cell
            cellId = cell["id"]
            cellType = cell["type"]
            if cellId not in listIdKnownNodes:
                listIdInvalidNodes.add(cellId)
            
            if cellId == self.userCell["id"]:
                nodeObject = PlayerNode(cell)
            elif cellId == self.enemyCell["id"]:
                nodeObject = EnemyNode(cell)
            elif cellId in self.listIdAgents:
                nodeObject = AgentNode(cell)
            elif cellType in listTypesSlider:
                nodeObject = SliderNode(cell)
            elif cellType == idBidirectional:
                nodeObject = BidirectionalNode(cell)
            elif cellType == idDeathPit:
                nodeObject = PitNode(cell)
            elif cellType in listIdTraps:
                nodeObject = TrapNode(cell)
            elif cellType == idSentryTurret:
                nodeObject = SentryNode(cell)
            elif cellType == idLesserObstacle:
                nodeObject = ObstacleNode(cell)
            elif cellType == idIce:
                nodeObject = IceNode(cell) 
            else:
                nodeObject = Node(cell)
            
            nodeObject.saveAdyacentConnections(self.map)
            idNode = nodeObject.id
            
            self.dictNodes[idNode] = nodeObject
            # Adding the pure node to the dictNodesPure, used to create connections of the skills like swap or toss
            self.dictNodesPure[idNode] = copy.deepcopy(nodeObject)
        
        # INFO: For some reason assigning the self.dictNodes to the nodeObject.dictGraphNodes in the previous loop cause the time to execute to skyrocket x40
        # This problem seems to be called "mutable default argument" or "mutable default parameter", thats is why its outside and must be outside
        for idNode, nodeObject in self.dictNodes.items():
            nodeObject.dictGraphNodes = self.dictNodes
        
        # Saving the nodes and setting the typeAgentIn in the nodes where the player, enemies and agents are
        self.saveNodesAndType()
        self.simpleSetType(self.dictNodesPure)
        
        # INFO: We loop again but after we created all the nodes since the next function access to the dictNodes
        for idNode, nodeObject in self.dictNodes.items():
            typeNode = nodeObject.typeNode
            
            # Deleting invalid/impossible connections
            if typeNode in listIdInvalidNodes:
                nodeObject.deleteConnections()
            else:
                nodeObject.deleteInvalidConnections(listIdInvalidNodes)
            
            # Saving id of the Goal cells and bidirectional cells
            if typeNode == 2:
                self.listIdGoals.append(idNode)
            elif typeNode == 11:
                is_charged = nodeObject.config["is_charged"]
                if is_charged is True:
                    self.listIdBidirectionals.append(idNode)
                    self.bidirectionalTileActive_flag = True
        
        # Creating connection between bidirectional cells and saving them
        if self.bidirectionalTileActive_flag is True and len(self.listIdBidirectionals) == 2:
            firstNode = self.dictNodes[self.listIdBidirectionals[0]]
            secondNode = self.dictNodes[self.listIdBidirectionals[1]]
            
            connectionOne = BidirectionalConnection(firstNode.cell, secondNode.cell, 0)
            connectionTwo = BidirectionalConnection(secondNode.cell, firstNode.cell, 0)
            
            firstNode.addConnection(connectionOne)
            secondNode.addConnection(connectionTwo)
            
            self.listConnectionsBidirectionals.append(connectionOne)
            self.listConnectionsBidirectionals.append(connectionTwo)
        
        # Saving player possible moves from the jsonResponse, usefull when the player is in a slider, also prevents the use of invalid movements and if its chossen 
        # as the goal node, adds to his pathConnections list the stay movement to keep him there
        possibleMoves = self.players["bearer"]["possible_moves"]
        self.userNode.savePossibleMoves(possibleMoves, self.map)
        self.userNode.deleteInvalidConnections(listIdInvalidNodes)
        
        # Creating copy of the listConnections in the AgentNodes (must be done after saving the nodes and types)
        self.enemyNode.copyListConnections()
        for id in self.listIdAgents:
            node = self.dictNodes[id]
            node.copyListConnections()
        
        # Checking if ryo is close to be trapped (sorrounded by an agent/enemy and with only one move), before this code was outside this class in the strategyPath function
        # but its more convenient doing the verification here
        ryoSorrounded_flag = False
        ryoCloseToPit = False
        ryoCloseToMine = False
        tmpList = list()
        for connection in self.ryoNode.listConnectionsCopy:
            nextNode = self.dictNodes[connection.toNode]
            if connection.toNode == self.enemyNode.id or connection.toNode in self.listIdAgents:
                ryoSorrounded_flag = True
                self.listIdAgentsSorrounding.append(connection.toNode)
                tmpList.append(connection)
            elif nextNode.typeNode == 12:
                ryoCloseToPit = True
                tmpList.append(connection)
            elif nextNode.typeNode == 14:
                ryoCloseToMine = True
                tmpList.append(connection)
            
        for connection in tmpList:
            self.ryoNode.listConnectionsCopy.remove(connection)
        
        confirmation_flag = False
        if ryoSorrounded_flag and len(self.ryoNode.listConnectionsCopy) == 1:
            nextNode = self.dictNodes[self.ryoNode.listConnectionsCopy[0].toNode]
            if type(nextNode) is SliderNode and nextNode.isCharged is True and len(nextNode.listConnections) > 0:
                if nextNode.toNode == self.ryoNode.id:
                    confirmation_flag = True
            else:
                confirmation_flag = True
                
        if confirmation_flag:
            self.ryoTrapped_flag = True
            self.ryoIdGoal = self.ryoNode.listConnectionsCopy[0].toNode
        
        self.ryoNode.copyListConnections()
        
        # Deleting the connections that points to agent nodes
        self.deleteConnectionsToAgentNodes(self.dictNodes)
        
    def saveCells(self) -> None:
        cell = self.getCell(self.players["bearer"]["position"])
        self.userCell = cell
        cell = self.getCell(self.players["opponent"]["position"])
        self.enemyCell = cell
        
        for agent in self.specialAgents:
            typeAgent = agent["type"]
            position = agent["position"]
            stats = agent
            if typeAgent == 1:
                self.ryoCell = self.getCell(position)
            elif typeAgent == 2:
                self.kixCell = self.getCell(position)
            elif typeAgent == 3:
                self.llamaCell = self.getCell(position)
            elif typeAgent == 4:
                self.ripperCell = self.getCell(position)
            elif typeAgent == 5:
                self.buzzCell = self.getCell(position)
            else:
                print(f"Unkown Agent!: {self.getCell(position)}")
            
            cell = self.getCell(position)
            self.dictAgentsCells[typeAgent] = {"cell": cell, "stats": stats}
            self.listIdAgents.append(cell["id"])
            
    def saveNodesAndType(self) -> None:
        self.userNode = self.dictNodes[self.userCell["id"]]
        self.userNode.setTypeAgentIn(100)
        self.userNode.saveStats(self.players["bearer"])
        self.enemyNode = self.dictNodes[self.enemyCell["id"]]
        self.enemyNode.setTypeAgentIn(200)
        self.enemyNode.saveStats(self.players["opponent"])
        
        for (typeAgent, info) in self.dictAgentsCells.items():
            cell = info["cell"]
            stats = info["stats"]
            agentNode = self.dictNodes[cell["id"]]
            if typeAgent == 1:
                self.ryoNode = agentNode
                self.ryoNode.saveStats(stats)
            elif typeAgent == 2:
                self.kixNode = agentNode
                self.kixNode.saveStats(stats)
            elif typeAgent == 3:
                self.llamaNode = agentNode
                self.llamaNode.saveStats(stats)
            elif typeAgent == 4:
                self.ripperNode = agentNode
                self.ripperNode.saveStats(stats)
            elif typeAgent == 5:
                self.buzzNode = agentNode
                self.buzzNode.saveStats(stats)
            else:
                print(f"Unkown Agent in Node!: {agentNode}")
    
    def simpleSetType(self, dictNodes: dict) -> None:
        userNode = dictNodes[self.userCell["id"]]
        userNode.setTypeAgentIn(100)
        enemyNode = dictNodes [self.enemyCell["id"]]
        enemyNode.setTypeAgentIn(200)
        
        for (typeAgent, info) in self.dictAgentsCells.items():
            cell = info["cell"]
            agentNode = dictNodes[cell["id"]]
            agentNode.setTypeAgentIn(typeAgent)
        
    # Function necessary to create a realistic map of nodes
    def deleteConnectionsToAgentNodes(self, dictNodes: dict) -> None:
        for (id, node) in dictNodes.items():
            tmpList = list()
            for connection in node.listConnections:
                nextNode = dictNodes[connection.toNode]
                if nextNode.typeAgentIn is not None and type(node) is not PlayerNode:
                    tmpList.append(connection)
                    node.listAgentConnections.append(connection)
                    
            for connection in tmpList:
                node.listConnections.remove(connection)
    
    def reverseDeleteAgentConnections(self):
        for (id, node) in self.dictNodes.items():
            for connection in node.listAgentConnections:
                node.listConnections.append(connection)
    
    # getCell() uses the x and y value (position), and returns the cell
    def getCell(self, position: dict) -> dict:
        try:
            x_value = position["x"]
        except TypeError as e:
            errorMsg = e.args[0]
            errorType = errorMsg[1:errorMsg.rfind("'")]
            if errorType == "NoneType":
                errorMsgReturn = "The position given is None Type, check that the jsonResponse you are passing to the Graph object is from a game in course!"
                raise TypeError(errorMsgReturn)
            else:
                raise TypeError(e)

        y_value= position["y"]
        cell = self.map[x_value][y_value]
        return cell
    
    # getNode() instead uses only the id of the node to retrive it from the dictNodes
    def getNode(self, idNode: int) -> Node:
        return self.dictNodes[idNode]
        
    # Returns a minimalist dictNodes with enough info to be used in getMap()
    @classmethod
    def getMiniDictNodes(klass, jsonResponse: dict) -> dict:
        players = jsonResponse["players"]
        specialAgents = jsonResponse["special_agents"]
        map = jsonResponse["map"]
        dictNodes = dict()
        
        playerPosition = players["bearer"]["position"]
        enemyPosition = players["opponent"]["position"]
        specialAgents = [agent for agent in specialAgents if agent["position"] is not None]
        listIdAgents = [getCell(agent["position"], map)["id"] for agent in specialAgents]
        
        listCells = [cell for column in map for cell in column]
        for cell in listCells:
            cellId = cell["id"]
            if cellId in listIdAgents:
                nodeObject = AgentNode(cell)
            else:
                nodeObject = Node(cell)
            
            dictNodes[cellId] = nodeObject
        
        if playerPosition:
            cell = getCell(playerPosition, map)
            playerNode = dictNodes[cell["id"]]
            playerNode.setTypeAgentIn(100)
        
        if enemyPosition:
            cell = getCell(enemyPosition, map)
            enemyNode = dictNodes[cell["id"]]
            enemyNode.setTypeAgentIn(200)
        
        # INFO: This asumes that the agent dict is the same as one of a game status = 1
        for agent in specialAgents:
            cell = getCell(agent["position"], map)
            agentNode = dictNodes[cell["id"]]
            agentNode.saveStats(agent)
            
        return dictNodes

    
def getCell(position: dict, map:list) -> dict:
    x_value = position["x"]
    y_value= position["y"]
    cell = map[x_value][y_value]
    return cell
        
def deleteConnectionsThatPointsToThisNode(idNode: int, dictNodes: dict):
    for (id, node) in dictNodes.items():
        tmpList = list()
        for connection in node.listConnections:
            if connection.toNode == idNode:
                tmpList.append(connection)
        
        for connection in tmpList:
            node.listConnections.remove(connection)
    

# This is the pure algorithm, if passed the pure argument to True, it will ignore the dangerous restricction, used for create possible connections of the skills
def pre_dijkstra(dictNodes: dict, idStart: int, idsGoal: list, pure=False, ignoreLandmines=True):
    listGoalNodes = list()
    
    for id in idsGoal:
        listGoalNodes.append(dictNodes[id])
        
    # Restoring values of the dictNodes in case they have already been processed by this function
    for (id, node) in dictNodes.items():
        node.deletePathConnections()
    
        
    listOpen = list()
    listClosed = list()
    
    startNode = dictNodes[idStart]
    startNode.setCostToReach(0)
    listOpen.append(startNode)
    Count = 0
    while len(listOpen) > 0:
        for node in listOpen:
            # This is the default behavior of dijkstra, no Death Pit node is calculate and by consecuence its not considered as a path in any case
            # NOTE: After checking again this code, i noticed this is redundant, it would be simpler just removing the pit listConnections like a 
            # wall node, but, i am not sure, since i want the dictNodes to be realistic this breaks this, since, its possible to go to this node but
            # not preferable, then this code suits well, i think?
            if type(node) is PitNode and pure is False:
                listOpen.remove(node)
                continue
            if pure is False and ignoreLandmines is False and node.typeNode == 14:
                listOpen.remove(node)
                continue
            # INFO: This method loads configuration depending of the type potential to salve a lot of things, experimental right now, it should be improvable
            node.loadUniqueConfig()
            """
            if type(node) is BidirectionalNode:
                print(node.id)
                print(node)
                print(node.pathConnections)"""
            Count = Count + 1
            listConnections = node.listConnections
            nodeCost = node.costToReach
            nodeListPath = node.pathConnections
            for connection in listConnections:
                if connection.ban is True:
                    continue
                
                costToReach = connection.cost + nodeCost
                
                nextNode = dictNodes[connection.toNode]
                nextNodeCost = nextNode.costToReach
                if nextNodeCost is None:
                    nodeListPath.append(connection)
                    nextNode.setCostToReach(costToReach)
                    nextNode.savePathConnections(nodeListPath)
                    listOpen.append(nextNode)
                    nodeListPath.remove(connection)
                else:
                    if costToReach >= nextNodeCost:
                        pass
                    elif costToReach < nextNodeCost:
                        nextNode.deletePathConnections()
                        if nextNode in listClosed:
                            listClosed.remove(nextNode)
                            listOpen.append(nextNode)
                        nodeListPath.append(connection)
                        nextNode.setCostToReach(costToReach)
                        nextNode.savePathConnections(nodeListPath)
                        nodeListPath.remove(connection)
                        
            listOpen.remove(node)
            listClosed.append(node)
    
    listFinal = list()
    for node in listGoalNodes:
        if node in listClosed:
            listFinal.append(node)
    
    winnerNode = None
    if len(listFinal) > 1:
        for node in listFinal:
            if winnerNode is None:
                winnerNode = node
            elif node.costToReach < winnerNode.costToReach:
                winnerNode = node
    elif len(listFinal) == 1:
        winnerNode = listFinal[0]
    
    # IMPROVE: If the goal nodes are unreachable the listFinal is empty, that it means we are sorrounded by obstacles type 17, 14, 1 or 3 if that happens we can 
    # only calculate a node far from the enemy if we are trapped with him, but i dont have good ideas of how do it, i will choose a random node until the obstacles 
    # type 17 dissapear or the match ends
    if len(listFinal) == 0:
        winnerNode = random.choice(listClosed)
    
    if type(winnerNode) is PlayerNode:
        winnerNode.playerNodeIsGoal()
        
    return winnerNode
    
# dijkstra will copy the dictNodes connections so the returned nodeGoal.pathConnections should not be trated as the same from the original dictNodes, this also means
# that the Nodes of original dictNodes doesnt have his dijkstra atributes with data, if you need to access to this processed info use pre_dijkstra, this is because the 
# following verifications modifies the nodes and since this function is going to be called more that one time not doing this could lead to create bad paths
def dijkstra(dictNodes: dict, idStart: int, idsGoal: list):
    dictNodesCopy = copy.deepcopy(dictNodes)
    x = InfinityDetector()
    
    nodeGoal = pre_dijkstra(dictNodesCopy, idStart, idsGoal)
    
    # Ripper Precaution
    # Ripper is instakill, getting too close is game over, i dont know when it targets the player or any agent so i cant create a perfect strategy to avoid him, what i 
    # can do is at least avoid fall in one of his adyacent nodes, to do this i will check if the first connection of the pathConnections points to one of his 4 adyacent
    # nodes if it does we deleted the connections that points to this node, unless its the exit of a ryoIdGoal
    ripperNode = None
    for (id, node) in dictNodesCopy.items():
        if node.typeAgentIn == 4:
            ripperNode = node
        
    if ripperNode is not None:
        while True:
            InfinityDetector.CountIter(x)
            nodeGoal = pre_dijkstra(dictNodesCopy, idStart, idsGoal)
            listRipperAdNodes = list()
            idDeathNode = None
            for connection in ripperNode.listConnections:
                listRipperAdNodes.append(connection.toNode)
            firstConn = nodeGoal.pathConnections[0]
            
            if firstConn.toNode in listRipperAdNodes:
                idDeathNode = firstConn.toNode
            
            if idDeathNode is None:
                break
            elif dictNodesCopy[idDeathNode].id in idsGoal:
                break
            else:
                deleteConnectionsThatPointsToThisNode(idDeathNode, dictNodesCopy)
    
    # Casting skill precaution (Uses previous nodeGoal value generated)
    # If the objective is 1 cell away and a skill will be used to reach it, it will ban this connection skill so it doesnt use it and it uses the normal move
    # IMPROVE: To ban, the id of the skill is connection is used, and is added here, would be better to use the list passed from the strategy code, but how?,
    # problems or more likely the not execution of this code are in the future if the id's are changed
    listIdMovementSkillsBan = [28]
    
    if len(nodeGoal.pathConnections) == 1 and nodeGoal.pathConnections[0].idSkill in listIdMovementSkillsBan:
        nodeGoal.pathConnections[0].setBan(True)
        nodeGoal = pre_dijkstra(dictNodesCopy, idStart, idsGoal)
    
    return nodeGoal

# Function to visualize the map in the console
def getMap(jsonResponse):
    # INFO: The dictNodes from the Graph.init() function is produced only if the json Responses are from states of games in course (status=1), 
    # this function solves this by creating a dictNodes depending in the state of the game
    listIdNOMAP = {-1, 0}
    if jsonResponse["state"]["status"] == 1:
        graphObject = Graph(jsonResponse)
        dictNodes = graphObject.dictNodes
    elif jsonResponse["state"]["status"] in listIdNOMAP:
        return "\nNO MAP\n"
    elif jsonResponse["state"]["status"] == 2:
        dictNodes = Graph.getMiniDictNodes(jsonResponse)
    else:
        return ("\nWARNING: UNKNOWN STATUS, NO MAP")
    
    map = jsonResponse["map"]
    lengColumn = len(map[0])
    
    mapStr = str()
    for num in range(lengColumn):
        for column in map:
            cell = column[num]
            currentNode = dictNodes[cell["id"]]
            typeNode = currentNode.typeNode
            typeAgentIn = currentNode.typeAgentIn
            if typeAgentIn is None:
                char = returnChar(typeNode, False)
            else:
                char = returnChar(typeAgentIn, True)
            mapStr = f"{mapStr}{char} "
        
        mapStr = f"{mapStr}\n"
            
    return mapStr
            
def returnChar(typeNode: int, isAgent: bool) -> str:
    character = None
    if isAgent is True:
        if typeNode == 1:
            character = "R"
        elif typeNode == 2:
            character = "K"
        elif typeNode == 3:
            character = "L"
        elif typeNode == 4:
            character = "!"
        elif typeNode == 5:
            character = "B"
        elif typeNode == 100:
            character = "P"
        elif typeNode == 200:
            character = "E"
        else:
            character = "?"
    else:
        if typeNode == 0:
            character = "+"
        elif typeNode == 1 or typeNode == 3:
            character = " "
        elif typeNode == 4 or typeNode == 5 or typeNode == 6:
            character = "="
        elif typeNode == 2:
            character = "#"
        elif typeNode == 7:
            character = "^"
        elif typeNode == 8:
            character = "~"
        elif typeNode == 9:
            character = "<"
        elif typeNode == 10:
            character = ">"
        elif typeNode == 11:
            character = "0"
        elif typeNode == 13:
            character = "$"
        elif typeNode == 12:
            character = "@"
        elif typeNode == 14:
            character = "*"
        elif typeNode == 15:
            character = "'"
        elif typeNode == 16:
            character = "{"
        elif typeNode == 17:
            character = "|"
        elif typeNode == 18:
            character = "%"
        else:
            character = "?"
    
    return character
