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
        self.id = self.cell["id"]
        self.type = self.cell["type"]
        self.position = self.cell["position"]
        self.config = self.cell["config"]
        self.listConnections = list()
        self.listAgentConnections = list()
        self.dictIdNearNodes = dict()
        self.typeAgentIn = None
        
        # Variables destined to use in the dijkstra algorithm
        self.costToReach = None
        self.pathConnections = list()
        
        
    def __repr__(self):
        return f"Node Id:{self.id} Type:{self.type} listConnections:{self.listConnections}"
        
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
        
    def setTypeAgentIn(self, type: int) -> None:
        self.typeAgentIn = type
    
    def setCostToReach(self, cost: int) -> None:
        self.costToReach = cost
    
    def savePathConnections(self, connections: list):
        for connection in connections:
            self.pathConnections.append(connection)
    
    def deletePathConnections(self):
        self.pathConnections = list()
        self.costToReach = None
        
# Complex Connections
# These connections can be created with nodes, as his name implies "nodeFrom", but it can also be created with cells, like a normal connnection but depending of
# the class of connection it could throw an error if depends of the data nodes (like AttackSkill)

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
        self.cost = cost


class MovementSkill(SkillConnection):
    def __init__(self, nodeFrom, nodeTo, infoSkill: dict, cost=1, usedSkill=True, idSkill=None, ban=False):
        super().__init__(nodeFrom, nodeTo, infoSkill, cost, usedSkill, idSkill, ban)


class AttackSKill(SkillConnection):
    def __init__(self, nodeFrom, nodeTo, infoSkill: dict, cost=1, usedSkill=True, idSkill=None, ban=False):
        super().__init__(nodeFrom, nodeTo, infoSkill, cost, usedSkill, idSkill, ban)
        self.damage = self.infoSkill["damage"]
        self.killConfirmation = False
        if self.damage >= self.nodeTo.totalLife:
            self.killConfirmation = True
    
    def __repr__(self):
        baseStr = f"#{self.fromNode}-{self.nodeFrom.nameAgent}--{self.cost}--{self.nodeTo.nameAgent}->{self.toNode} SKILL: {self.nameSkill}"
        
        if self.killConfirmation is True:
            baseStr = f"{baseStr} KILL!!"
        if self.ban:
            baseStr = f"{baseStr} BANNED"
        baseStr = f"{baseStr}#"
        
        return baseStr

# Complex Nodes

class ChildNode(Node):
    def __init__(self, node: Node):
        super().__init__(node.cell)
        self.listConnections = node.listConnections
        self.dictIdNearNodes = node.dictIdNearNodes
        self.typeAgentIn = node.typeAgentIn
        
        self.costToReach = node.costToReach
        self.pathConnections = node.pathConnections
        

class SliderNode(ChildNode):
    def __init__(self, node: Node):
        super().__init__(node)
        self.isCharged = self.config["is_charged"]
        self.toNode = None
        
    def deleteInvalidConnections(self, listIds: list) -> None:
        charged = self.config["is_charged"]
            
        tmpList = list()
        if charged is False:
            pass
        elif self.type == 7 and self.dictIdNearNodes["up"] is not None:
            for connection in self.listConnections:
                if connection.toNode != self.dictIdNearNodes["up"]:
                    tmpList.append(connection)
        elif self.type == 8 and self.dictIdNearNodes["down"] is not None:
            for connection in self.listConnections:
                if connection.toNode != self.dictIdNearNodes["down"]:
                    tmpList.append(connection)
        elif self.type == 9 and self.dictIdNearNodes["left"] is not None:
            for connection in self.listConnections:
                if connection.toNode != self.dictIdNearNodes["left"]:
                    tmpList.append(connection)
        elif self.type == 10 and self.dictIdNearNodes["right"] is not None:
            for connection in self.listConnections:
                if connection.toNode != self.dictIdNearNodes["right"]:
                    tmpList.append(connection)
        else:
            self.deleteConnections()
        
        for connection in tmpList:
            self.listConnections.remove(connection)
        
        tmpList = list()
        for connection in self.listConnections:
            if connection.typeToNode in listIds:
                tmpList.append(connection)
        
        for connection in tmpList:
            self.listConnections.remove(connection)
        
        for connection in self.listConnections:
            connection.setCost(0)
            self.toNode = connection.toNode

class DangerousNode(ChildNode):
    def __init__(self, node: Node):
        super().__init__(node)
        

class BidirectionalNode(ChildNode):
    def __init__(self, node: Node):
        super().__init__(node)
        self.isCharged = self.config["is_charged"]
        

class PlayerNode(ChildNode):
    def __init__(self, node: Node):
        super().__init__(node)
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
        self.nameAgent = dictStats["name"]
        self.armor = dictStats["stats"]["armor"]
        self.hitpoints = dictStats["stats"]["hitpoints"]
        
        self.totalLife = self.armor + self.hitpoints
        
            
class AgentNode(ChildNode):
    def __init__(self, node: Node):
        super().__init__(node)
        self.listConnectionsCopy = list()
        self.totalLife = None
        
    def copyListConnections(self):
        self.listConnectionsCopy = copy.deepcopy(self.listConnections)
    
    def saveStats(self, dictStats: dict):
        self.nameAgent = dictStats["name"]
        self.armor = dictStats["stats"]["armor"]
        self.hitpoints = dictStats["stats"]["hitpoints"]
        
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

        # IMPROVE: Right now the code its updated so all the nodes are treated in the right way, but if the devs update the game
        # with new cells then there is the possibility of creating invalid connections, the ideal solution would be check first if the node
        # its a known node if not then it should be treated as an invalid node to prevent bugs
        listIdInvalidNodes = [1, 3, 16, 17] # 12: Death Pit  13: Zap Trap  14: Mine  17: Lesser Obstacle  15: Bobby trap  16: Sentry Turret
        listTypesSlider = [7, 8, 9, 10]
        listDangerousNodes = [12, 14]
        for cell in listCells:
            # No matter the type of the cell its added to the dictNodes, the key is the unique id and the value is a nade object with a list of  
            # connections that could be empty or with the connections if its a valid cell
            nodeObject = Node(cell)
            nodeObject.saveAdyacentConnections(self.map)
            typeNode = nodeObject.type
            idNode = nodeObject.id
            
            # IMPROVE: This could be improved, instead of converting after the nodes objects to his type it could be done before creating the node, with the cell
            if cell["type"] in listTypesSlider:
                nodeObject = SliderNode(nodeObject)
            elif cell["type"] in listDangerousNodes:
                nodeObject = DangerousNode(nodeObject)
            elif cell["type"] == 11:
                nodeObject = BidirectionalNode(nodeObject)
            
            # Adding the pure node to the dictNodesPure, used to create connections of the skills like swap or toss
            self.dictNodesPure[idNode] = copy.deepcopy(nodeObject)
            
            if typeNode in listIdInvalidNodes:
                nodeObject.deleteConnections()
            else:
                nodeObject.deleteInvalidConnections(listIdInvalidNodes)
            
            if idNode == self.userCell["id"]:
                nodeObject = PlayerNode(nodeObject)
            elif idNode == self.enemyCell["id"]:
                nodeObject = AgentNode(nodeObject)
            elif idNode in self.listIdAgents:
                nodeObject = AgentNode(nodeObject)
            
            dictNodes[idNode] = nodeObject
            
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
            firstNode = dictNodes[self.listIdBidirectionals[0]]
            secondNode = dictNodes[self.listIdBidirectionals[1]]
            
            connectionOne = Connection(firstNode.cell, secondNode.cell, 0)
            connectionTwo = Connection(secondNode.cell, firstNode.cell, 0)
            
            firstNode.addConnection(connectionOne)
            secondNode.addConnection(connectionTwo)
            
            self.listConnectionsBidirectionals.append(connectionOne)
            self.listConnectionsBidirectionals.append(connectionTwo)
        
        # Saving the nodes and setting the typeAgentIn in the nodes where the player, enemies and agents are
        self.saveNodesAndType(dictNodes)
        self.simpleSetType(self.dictNodesPure)
        
        # Saving player possible moves from the jsonResponse, usefull when the player is in a slider, also prevents the use of invalid movements and if its chossen 
        # as the goal node, adds to his pathConnections list the stay movement to keep him there
        possibleMoves = self.players["bearer"]["possible_moves"]
        self.userNode.savePossibleMoves(possibleMoves, self.map)
        self.userNode.deleteInvalidConnections(listIdInvalidNodes)
        
        # Creating copy of the listConnections in the AgentNodes (must be done after saving the nodes and types)
        self.enemyNode.copyListConnections()
        for id in self.listIdAgents:
            node = dictNodes[id]
            node.copyListConnections()
        
        # Checking if ryo is close to be trapped (sorrounded by an agent/enemy and with only one move), before this code was outside this class in the strategyPath function
        # but its more convenient doing the verification here
        ryoSorrounded_flag = False
        ryoCloseToPit = False
        ryoCloseToMine = False
        tmpList = list()
        for connection in self.ryoNode.listConnectionsCopy:
            nextNode = dictNodes[connection.toNode]
            if connection.toNode == self.enemyNode.id or connection.toNode in self.listIdAgents:
                ryoSorrounded_flag = True
                self.listIdAgentsSorrounding.append(connection.toNode)
                tmpList.append(connection)
            elif nextNode.type == 12:
                ryoCloseToPit = True
                tmpList.append(connection)
            elif nextNode.type == 14:
                ryoCloseToMine = True
                tmpList.append(connection)
            
        for connection in tmpList:
            self.ryoNode.listConnectionsCopy.remove(connection)
        
        confirmation_flag = False
        if ryoSorrounded_flag and len(self.ryoNode.listConnectionsCopy) == 1:
            nextNode = dictNodes[self.ryoNode.listConnectionsCopy[0].toNode]
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
        self.deleteConnectionsToAgentNodes(dictNodes)
        
        # Binding at the end the self.dictNodes with the dictNodes for convenience 
        self.dictNodes = dictNodes
        
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
            
    def saveNodesAndType(self, dictNodes: dict) -> None:
        self.userNode = dictNodes[self.userCell["id"]]
        self.userNode.setTypeAgentIn(100)
        self.userNode.saveStats(self.players["bearer"])
        self.enemyNode = dictNodes[self.enemyCell["id"]]
        self.enemyNode.setTypeAgentIn(200)
        self.enemyNode.saveStats(self.players["opponent"])
        
        for (type, info) in self.dictAgentsCells.items():
            cell = info["cell"]
            stats = info["stats"]
            agentNode = dictNodes[cell["id"]]
            agentNode.setTypeAgentIn(type)
            if type == 1:
                self.ryoNode = agentNode
                self.ryoNode.saveStats(stats)
            elif type == 2:
                self.kixNode = agentNode
                self.kixNode.saveStats(stats)
            elif type == 3:
                self.llamaNode = agentNode
                self.llamaNode.saveStats(stats)
            elif type == 4:
                self.ripperNode = agentNode
                self.ripperNode.saveStats(stats)
            elif type == 5:
                self.buzzNode = agentNode
                self.buzzNode.saveStats(stats)
            else:
                print(f"Unkown Agent in Node!: {agentNode}")
    
    def simpleSetType(self, dictNodes: dict) -> None:
        userNode = dictNodes[self.userCell["id"]]
        userNode.setTypeAgentIn(100)
        enemyNode = dictNodes [self.enemyCell["id"]]
        enemyNode.setTypeAgentIn(200)
        
        for (type, info) in self.dictAgentsCells.items():
            cell = info["cell"]
            agentNode = dictNodes[cell["id"]]
            agentNode.setTypeAgentIn(type)
        
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
        x_value = position["x"]
        y_value= position["y"]
        cell = self.map[x_value][y_value]
        return cell
    
    # getNode() instead uses only the id of the node to retrive it from the dictNodes
    def getNode(self, idNode: int) -> Node:
        return self.dictNodes[idNode]

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
def pre_dijkstra(dictNodes: dict, idStart: int, idsGoal: list, pure=False):
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
    
    while len(listOpen) > 0:
        for node in listOpen:
            # This is the default behavior of dijkstra, no dangerous node is calculate and by consecuence its not considered as a path in any case
            if type(node) is DangerousNode and pure is False:
                listOpen.remove(node)
                continue
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
    
    listBiNodes = list()
    # This Checks if the bidirectional nodes were used and the way they were used, and re-calculate if neccesary, should loop a maximum of 2 times
    while True:
        InfinityDetector.CountIter(x)
        usedBiNode_flag = False
        usedBiConn_flag = False
        nodeGoal = pre_dijkstra(dictNodesCopy, idStart, idsGoal)
        for connection in nodeGoal.pathConnections:
            nextNode = dictNodesCopy[connection.toNode]
            if type(nextNode) is BidirectionalNode:
                listBiNodes.append(nextNode)
                usedBiNode_flag = True
            if connection.typeFromNode == 11 and connection.typeToNode == 11:
                usedBiConn_flag = True
    
        if usedBiNode_flag is True and usedBiConn_flag is False:
            for node in listBiNodes:
                deleteConnectionsThatPointsToThisNode(node.id, dictNodesCopy)
        else:
            break
    
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
    graphObject = Graph(jsonResponse)
    dictNodes = graphObject.dictNodes
    map = graphObject.map
    lengColumn = len(map[0])
    
    mapStr = str()
    for num in range(lengColumn):
        for column in map:
            cell = column[num]
            currentNode = dictNodes[cell["id"]]
            type = currentNode.type
            typeAgentIn = currentNode.typeAgentIn
            if typeAgentIn is None:
                char = returnChar(type, False)
            else:
                char = returnChar(typeAgentIn, True)
            mapStr = f"{mapStr}{char} "
        
        mapStr = f"{mapStr}\n"
            
    return mapStr
            
def returnChar(type: int, isAgent: bool) -> str:
    character = None
    if isAgent is True:
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
        else:
            character = "?"
    else:
        if type == 0:
            character = "+"
        elif type == 1 or type == 3:
            character = " "
        elif type == 4 or type == 5 or type == 6:
            character = "="
        elif type == 2:
            character = "#"
        elif type == 7:
            character = "^"
        elif type == 8:
            character = "~"
        elif type == 9:
            character = "<"
        elif type == 10:
            character = ">"
        elif type == 11:
            character = "0"
        elif type == 13:
            character = "$"
        elif type == 12:
            character = "@"
        elif type == 14:
            character = "*"
        elif type == 15:
            character = "'"
        elif type == 16:
            character = "{"
        elif type == 17:
            character = "|"
        else:
            character = "?"
    
    return character
