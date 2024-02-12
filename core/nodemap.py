# Version 2.0 
# The first version of this code was made with the intention of not spend too much memory, the result was an awfull code because there was a lot of errors, 
# this version creates a lot of classes and uses a lot of loops sometimes so its probably going to use much memory, the advantajes is better readability, 
# defines (hopefully permanently) the basic structure and best way of create the graph, nodes and connections objects to be easy modifiable in case is needed
import random
import copy
import time

from config import KEEPMOVESKILL

class Connection():
    def __init__(self, cellFrom: dict, cellTo: dict, cost=1, usedSkill=False, idSkill=None, ban=False, direction=None):
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
        self.direction = direction
        # If a string is added to this variable, it will be printed
        self.notes = None
    
    def __repr__(self):
        baseStr = f"#{self.fromNode}-{self.typeFromNode}--{self.cost}--{self.typeToNode}->{self.toNode}"
        if self.usedSkill:
            baseStr = f"{baseStr} Skill Used"
        if self.ban:
            baseStr = f"{baseStr} BANNED"
        if type(self.notes) is str:
            baseStr = f"{baseStr} {self.notes}"
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

# A custom list class that saves an id of his corresponding map and info about the path
class Path(list):
    def __init__(self, *args, **kwargs):
        self.idMap_ = 0
        
        # If the path is longer of 1 connection this variable will always be non None
        self.typeEndsOn_ = None
        
        # Only if the path is longer that 2 connection, this info will be not None or not empty
        self.typesInPath_ = list()
        self.isClear_ = None
        self.isSemiClear_ = None
        self.isDirect_ = None
        
        self.dictGraphNodes_ = None
        
        super().__init__(*args, **kwargs)
    
    def _createInfoPath(self):
        if len(self) == 0:
            return None
        
        for connection in self:
            if connection is not self[-1]:
                self.typesInPath_.append(type(self.dictGraphNodes_[connection.toNode]))
            else:
                self.typeEndsOn_ = type(self.dictGraphNodes_[connection.toNode])
        
        # We consider as a 'clear' path if there is only blank tiles or the player is on it
        allowedTypes = [Node, PlayerNode]
        for typeNode in self.typesInPath_:
            if typeNode in allowedTypes:
                self.isClear_ = True
            else:
                self.isClear_ = False
                break
        
        # We consider as a 'semi-clear' path if there is no obstacles/walls in the path but accepts special tiles like traps as 'clear'
        for typeNode in self.typesInPath_:
            if isinstance(typeNode, BlockNode) is False:
                self.isSemiClear_ = True
            else:
                self.isSemiClear_ = False
                break
        
        previousDirection = None
        for connection in self:
            currentDirection = connection.direction
            if previousDirection is None:
                previousDirection = currentDirection
                continue
            
            if currentDirection == previousDirection:
                self.isDirect_ = True
            else:
                self.isDirect_ = False
                break


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
        
        self.notes = None
        
        self.idsRange1 = list()
        self.idsRange2 = list()
        self.idsRange2direct = list()
        self.idsRange2indirect = list()
        self.idsRange2directClear = list()
        self.idsRange2directSemiClear = list()
        
        # Each Node has access to the graphs, making easy the access to info about all the nodes
        self.dictGraphNodes = None
        self.dictGraphNodesPure = None
        self.dictGraphNodesPureAll1 = None
        
        # Variables destined to use in the dijkstra algorithm
        self.costToReach = None
        self.pathConnections = Path()
        self.idMap = 0
        
        
    def __repr__(self):
        return f"Node Id:{self.id} Type:{self.typeNode} listConnections:{self.listConnections} idMap:{self.idMap}"
        
    def saveAdyacentConnections(self, map: list) -> None:
        x_value = self.position["x"]
        y_value = self.position["y"]
        dictIdNearNodes = dict()
        listCells = list()
        try:
            cell_right = map[x_value + 1][y_value]
            listCells.append((cell_right, "right"))
            dictIdNearNodes["right"] = cell_right["id"]
        except IndexError:
            dictIdNearNodes["right"] = None
        try:
            cell_down = map[x_value][y_value + 1]
            listCells.append((cell_down, "down"))
            dictIdNearNodes["down"] = cell_down["id"]
        except IndexError:
            dictIdNearNodes["down"] = None
        if x_value > 0:
            cell_left = map[x_value - 1][y_value]
            listCells.append((cell_left, "left"))
            dictIdNearNodes["left"] = cell_left["id"]
        else:
            dictIdNearNodes["left"] = None
        if y_value > 0:
            cell_up = map[x_value][y_value - 1]
            listCells.append((cell_up, "up"))
            dictIdNearNodes["up"] = cell_up["id"]
        else:
            dictIdNearNodes["up"] = None
        
        self.dictIdNearNodes = dictIdNearNodes
        for cell, direction in listCells:
            connection = Connection(self.cell, cell, direction=direction)
            self.listConnections.append(connection)
    
    def deleteInvalidConnections(self, listIds: list) -> None:
        tmpList = list()
        for connection in self.listConnections:
            if connection.typeToNode in listIds:
                tmpList.append(connection)
        
        for connection in tmpList:
            self.listConnections.remove(connection)
    
    def assingDictPointerToPath(self):
        self.pathConnections.dictGraphNodes_ = self.dictGraphNodes
        #print(type(self.dictGraphNodes))
    
    def _createAndAppend(self, fCell, sCell, direction):
        connection = Connection(self.cell, cell)
        self.listConnections.append(connection)
    
    def createIdsRangeInfo(self):
        pure_Dijkstra(self.dictGraphNodesPureAll1, [], self.id, limit=3)
        #print(self.typeAgentIn, self.id)
        for idNode, node in self.dictGraphNodesPureAll1.items():
            if node.costToReach == 1:
                self.idsRange1.append(idNode)
            elif node.costToReach == 2:
                self.idsRange2.append(idNode)
                previousDirection = None
        
        range2Nodes = [self.dictGraphNodesPureAll1[idNode] for idNode in self.idsRange2]
        for node in range2Nodes:
            node.assingDictPointerToPath()
            node.pathConnections._createInfoPath()
            pathConnections = node.pathConnections
            if pathConnections.isDirect_ is False:
                self.idsRange2indirect.append(pathConnections[-1].toNode)
            elif pathConnections.isDirect_ is True and pathConnections.isClear_ is True:
                self.idsRange2directClear.append(pathConnections[-1].toNode)
            elif pathConnections.isDirect_ is True and pathConnections.isClear_ is False:
                self.idsRange2direct.append(pathConnections[-1].toNode)
            
            if pathConnections.isDirect_ is True and pathConnections.isSemiClear_ is True:
                self.idsRange2directSemiClear.append(pathConnections[-1].toNode)
        #print("DONE!")
    
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
    
    def saveInfoPath(self, cost: int, pathNode: Path, connFrom: Connection): # Path: list
        self.costToReach = cost
        for connection in pathNode:
            self.pathConnections.append(connection)
        self.pathConnections.append(connFrom)
    
    def deleteInfoPath(self):
        self.pathConnections = Path()
        self.costToReach = None
    
    def deletePathConnections(self):
        self.pathConnections = Path()
        self.costToReach = None
    
    def loadUniqueConfig(self):
        return None
    
    def confirmChanges(self):
        return None
    
    def removeUniqueConfig(self):
        return None
    
    @classmethod
    # This path has no info about his .dictGraphNodes variables
    def createTmpPath(klass, pathNode: Path, connFrom: Connection):
        path = Path()
        for connection in pathNode:
            path.append(connection)
        path.append(connFrom)
        
        return path

# Map is the dict of nodes with an unique id that is meant to be used in dijkstra algorithm
class Map(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.idMap_ = 0
    
    def updateId(self, newId: int) -> None:
        for id, node in self.items():
            node.idMap = newId
        self.idMap_ = newId
    
# Complex Connections
# These connections can be created with nodes, as his name implies "nodeFrom", but it can also be created with cells, like a normal connnection but depending of
# the class of connection it could throw an error if depends of the data nodes (like AttackSkill)

class SkillCellConnection(Connection):
    def __init__(self, nodeFrom, nodeTo, cost=1, usedSkill=False, idSkill=None, ban=False):
        if type(nodeFrom) is dict and type(nodeTo) is dict:
            super().__init__(nodeFrom, nodeTo, cost, usedSkill, idSkill, ban)
        elif isinstance(nodeFrom, Node) and isinstance(nodeTo, Node):
            super().__init__(nodeFrom.cell, nodeTo.cell, cost, usedSkill, idSkill, ban)
            self.nodeFrom = nodeFrom
            self.nodeTo = nodeTo
        else:
            raise ValueError("Type of Nodes/Cells is wrong, please check those values")

class BidirectionalConnection(SkillCellConnection):
    def __init__(self, nodeFrom, nodeTo, cost=1, usedSkill=False, idSkill=None, ban=False):
        # This format must be changed, instead of relying in putting the variables in the right order, its must be passed in keywords to prevent bugs
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

# General characteristic class

class SpecialTileNode(ChildNode):
    def __init__(self, cell: dict):
        super().__init__(cell)

class BlockNode(ChildNode):
    def __init__(self, cell: dict):
        super().__init__(cell)

# ---

class ObstacleNode(BlockNode):
    def __init__(self, cell: dict):
        super().__init__(cell)


class ExitNode(SpecialTileNode):
    def __init__(self, cell: dict):
        super().__init__(cell)
        self.isCharged = self.config["is_charged"]


class WallNode(BlockNode):
    def __init__(self, cell: dict):
        super().__init__(cell)

class RegeneratorNode(SpecialTileNode):
    def __init__(self, cell: dict):
        super().__init__(cell)

class SliderNode(SpecialTileNode):
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
        # deleting the connections (uniqueSliderConn) must be changed
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
            # 100 is User Node, specifiying because it should not delete if its ponting to other agents but if its the player it must delete
            if nextNodeAgent is not None and nextNodeAgent != 100:
                deleteConn_flag = False
            elif nextNodeType in listIds:
                deleteConn_flag = False
        
        if deleteConn_flag:
            for connection in tmpList:
                self.listConnections.remove(connection)
        """
        # If deleteConn_flag is False it wont remove the rest of connections and is like if the node were non charged, this variable is used in
        # swap to verify valid swap pseudo-skill connections, but if deleteConn_flag is false, the pseudo-skill wont be be added even tho
        # its possible but not since it uses charged variable, i am adding this only as a reminder of this, i dont think its the best
        
        else:
            self.isCharged = False
        """
        
    
class BidirectionalNode(SpecialTileNode):
    def __init__(self, cell: dict):
        super().__init__(cell)
        self.isCharged = self.config["is_charged"]
        self.twinNodeId = None
    
    def loadUniqueConfig(self):
        if self.isCharged is False:
            return None
        
        tmpList = [connection for connection in self.listConnections if type(connection) is not BidirectionalConnection]
        for connection in tmpList:
            self.listConnections.remove(connection)
        
        self.isCharged = False
        
        twinNode = self.dictGraphNodes[self.twinNodeId]
        twinNode.isCharged = False
        
        twinBiConn = [connection for connection in twinNode.listConnections if type(connection) is BidirectionalConnection]
        twinNode.listConnections.remove(twinBiConn[0])
    
    def confirmChanges(self):
        return self.isCharged
    
class PitNode(ChildNode):
    def __init__(self, cell: dict):
        super().__init__(cell)

class TrapNode(ChildNode):
    def __init__(self, cell: dict):
        super().__init__(cell)

class SentryNode(BlockNode):
    def __init__(self, cell: dict):
        super().__init__(cell)

class LesserObsNode(BlockNode):
    def __init__(self, cell: dict):
        super().__init__(cell)

class IceNode(ChildNode):
    def __init__(self, cell: dict):
        super().__init__(cell)
        self.tmpListConnections = list()
        self.redirects = False
    
    def saveAdyacentConnections(self, map: list) -> None:
        super().saveAdyacentConnections(map)
        
        for connection in self.listConnections:
            connection.setCost(0)
            self.toNode = connection.toNode
    
    def loadUniqueConfig(self):
        fromNodeId = self.pathConnections[-1].fromNode
        dictIdNearNodes = {idNode: direction  for direction, idNode in self.dictIdNearNodes.items()}
        
        inamovibleTypeNodes = [AgentNode, EnemyNode, ObstacleNode, WallNode, SentryNode, LesserObsNode]
        redirectRules = {"down": "up", "right": "left", "left": "right", "up": "down"}
        # Only movements from adyacent nodes are valid
        if fromNodeId in dictIdNearNodes:
            direction = dictIdNearNodes[fromNodeId]
            validConnectionId = self.dictIdNearNodes[redirectRules[direction]]
            # IF is the validConnectionId is None, there is no Node in that direction
            if not validConnectionId:
                pass
            elif type(self.dictGraphNodes[validConnectionId]) in inamovibleTypeNodes:
                pass
            else:
                tmpList = [connection for connection in self.listConnections if connection.toNode != validConnectionId]
                for connection in tmpList:
                    self.listConnections.remove(connection)
                    self.tmpListConnections.append(connection)
                self.redirects = True
        
        return True
    
    def removeUniqueConfig(self):
        for connection in self.tmpListConnections:
            self.listConnections.append(connection)
        self.tmpListConnections = list()
        self.redirects = False
    
    # It creates a temporary copy of itself to check if it redirects depending of the path
    # FIX: This consumes a lot of processing power if the map has a lot of ice tiles, not idea how to solve it
    def redirectsTo(self, pathNode: Node, connectionFrom: Connection):
        tmpSelfCopy = copy.deepcopy(self)
        tmpSelfCopy.deletePathConnections()
        tmpSelfCopy.saveInfoPath(cost=None, pathNode=pathNode, connFrom=connectionFrom)
        tmpSelfCopy.loadUniqueConfig()
        
        if tmpSelfCopy.redirects is True:
            return tmpSelfCopy.listConnections[0]
        else:
            return None

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
        self.playerStats = dictStats
        self.nameNode = dictStats["name"]
        self.armor = dictStats["stats"]["armor"]
        self.hitpoints = dictStats["stats"]["hitpoints"]
        
        self.totalLife = self.armor + self.hitpoints

class EntityNode(BlockNode):
    def __init__(self, cell: dict):
        super().__init__(cell)

class EnemyNode(EntityNode):
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

class AgentNode(EntityNode):
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
        
        # Dijkstra Variables
        self.dictMaps = dict()
        
        # Saving cells of player and agents
        self.saveCells()
        
        # Flag to confirme the status of the bidirectional tiles
        self.bidirectionalTileActive_flag = False
        
        self.listIdBidirectionals = list()
        self.listConnectionsBidirectionals = list()
        self.listIdGoals = list()
        self.dictNodes = Map()
        self.dictNodesPure = Map()
        self.dictNodesPureAll1 = Map()
        
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
        idObstacle = 1
        idExit = 2
        idWall = 3
        listIdRegenerators = {4, 5, 6}
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
            elif cellType == idObstacle:
                nodeObject = ObstacleNode(cell)
            elif cellType == idExit:
                nodeObject = ExitNode(cell)
            elif cellType == idWall:
                nodeObject = WallNode(cell)
            elif cellType in listIdRegenerators:
                nodeObject = RegeneratorNode(cell)
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
                nodeObject = LesserObsNode(cell)
            elif cellType == idIce:
                nodeObject = IceNode(cell) 
            else:
                nodeObject = Node(cell)
            
            nodeObject.saveAdyacentConnections(self.map)
            idNode = nodeObject.id
            
            self.dictNodes[idNode] = nodeObject
        
        # Creating a dictNodesPure and dictNodesPureAll1, used to create connections of the skills like swap or toss
        # dictNodesPureAll1 is a dictNodes with all the connections cost set to 1
        self.dictNodesPure = copy.deepcopy(self.dictNodes)
        self.dictNodesPureAll1 = copy.deepcopy(self.dictNodes)
        
        # Setting all the connections cost to 1
        for idNode, node in self.dictNodesPureAll1.items():
            for connection in node.listConnections:
                connection.setCost(1)
        
        # INFO: For some reason assigning the self.dictNodes to the nodeObject.dictGraphNodes in the previous nodeObject creation loop cause the time to execute to skyrocket x40
        # This problem seems to be called "mutable default argument" or "mutable default parameter", thats is why its outside and must be outside
        for idNode, nodeObject in self.dictNodes.items():
            nodeObject.dictGraphNodes = self.dictNodes
            nodeObject.dictGraphNodesPure = self.dictNodesPure
            nodeObject.dictGraphNodesPureAll1 = self.dictNodesPureAll1
        
        for idNode, nodeObject in self.dictNodesPure.items():
            nodeObject.dictGraphNodes = self.dictNodes
            nodeObject.dictGraphNodesPure = self.dictNodesPure
            nodeObject.dictGraphNodesPureAll1 = self.dictNodesPureAll1
        
        for idNode, nodeObject in self.dictNodesPureAll1.items():
            nodeObject.dictGraphNodes = self.dictNodes
            nodeObject.dictGraphNodesPure = self.dictNodesPure
            nodeObject.dictGraphNodesPureAll1 = self.dictNodesPureAll1
        
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
            if type(nodeObject) is ExitNode and nodeObject.isCharged is True:
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
            
            firstNode.twinNodeId = secondNode.id
            secondNode.twinNodeId = firstNode.id
            
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
        
        # Creating copy of the listConnections in the AgentNodes (must be done after saving the nodes and types). Used for the next block
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
        
        # Creating the idsRange info of the entity nodes (player is not included)
        self.createRangeInfoEntities()
        
        # Saving the original dictNodes
        self.dictMaps[0] = self.dictNodes
        
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
                # If the nextNode is the PlayerNode is bypassed, because in theory we can return to our cell, and also solves a bug of dijkstra when handling
                # the IceNode(this is the major reason actuallly). If we do this we are going to break the code so thats why a elif block is added
                if nextNode.typeAgentIn is not None and type(nextNode) is not PlayerNode:
                    tmpList.append(connection)
                    node.listAgentConnections.append(connection)
                elif nextNode.typeAgentIn is not None and type(nextNode) is PlayerNode and isinstance(node, EntityNode) is True:
                    tmpList.append(connection)
                    node.listAgentConnections.append(connection)
            
            for connection in tmpList:
                node.listConnections.remove(connection)
    
    def createRangeInfoEntities(self):
        listEntityNodes = [self.enemyNode, self.ryoNode, self.kixNode, self.llamaNode, self.ripperNode, self.buzzNode]
        for entityNode in listEntityNodes:
            if entityNode is not None:
                entityNode.createIdsRangeInfo()
        
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
        
    
    def loadMap(self, node:Node):
        idMap = node.idMap
        
        if idMap == self.dictNodes.idMap_:
            pass
        else:
            self.dictNodes = self.dictMaps[idMap]
    
    def createMap(self, node: Node):
        newKey = list(self.dictMaps.keys())[-1] + 1
        
        mapCopy = copy.deepcopy(self.dictNodes)
        mapCopy.updateId(newKey)
        mapCopy[node.id].loadUniqueConfig()
        self.dictMaps[newKey] = mapCopy
        
        # Reseting all the nodes path info, cost, if are not from the path of this generator node
        idsPath = [connection.fromNode for connection in node.pathConnections]
        idsPath.append(node.id)
        for id, nodeCopy in mapCopy.items():
            if id in idsPath:
                continue
            nodeCopy.deletePathConnections()
        
        return mapCopy[node.id]
        
    def loadExternalConfigs(self, node: Node):
        # This makes sure a generator node its not processed here
        if node.confirmChanges() is True:
            return None
        
        node.loadUniqueConfig()
        # IMPROVE: Since this is called everytime a node is processed in the listOpen, it probably consumes a lot of processing power, it should be a better way
        for id, dNode in self.dictNodes.items():
            if dNode == node:
                continue
            dNode.removeUniqueConfig()
    
    def resetMaps(self):
        self.dictMaps = {0: self.dictMaps[0]}
        for nodeId, node in self.dictMaps[0].items():
            node.deleteInfoPath()
        self.dictNodes = self.dictMaps[0]
    
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
            # For some reason if the game has ended status: 2 the positionof the enemy no longer conrrespond to the map so it raises a error
            try:
                cell = getCell(enemyPosition, map)
                enemyNode = dictNodes[cell["id"]]
                enemyNode.setTypeAgentIn(200)
            except IndexError:
                pass
        
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
    
# Class made to find the nodes that are re-added to the open list (when a short path has been found)
class OpenList(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.firstAdd_ = set()
        self.removed_ = set()
        self.reAdded_ = set()
        
    def append(self, item):
        super().append(item)
        if item in self.removed_:
            self.reAdded_.add(item)
        self.firstAdd_.add(item)
    
    def remove(self, item):
        super().remove(item)
        self.removed_.add(item)
    
    # idMap = None to print nodes from all the maps
    def getreadded_(self, idMap=0, onlyIds=True):
        if idMap == None and onlyIds is True:
            return [item.id for item in self.reAdded_]
        elif idMap == None and onlyIds is False:
            return [item for item in self.reAdded_]
        elif onlyIds is True:
            return [item.id for item in self.reAdded_ if item.idMap == idMap]
        elif onlyIds is False:
            return [item for item in self.reAdded_ if item.idMap == idMap]
        

# The main dijkstra function, it creates new maps (dictNodes) depending of where the bot goes and it returns the less cost path to the objective
def pre_dijkstra(graphObject: Graph, idsGoal: list, idStart=None):
    if idStart is None:
        idStart = graphObject.userNode.id
        
    # Restoring values of the dictNodes in case they have already been processed by this function
    graphObject.resetMaps()
        
    listOpen = OpenList()
    listClosed = list()
    
    startNode = graphObject.dictNodes[idStart]
    startNode.setCostToReach(0)
    listOpen.append(startNode)
    Count = 0
    while len(listOpen) > 0:
        for node in listOpen:
            #print(f"\nNEXT NODE ITER: {node}\n{node.pathConnections}")#\nOPEN LIST: {[[item.id, item.idMap] for item in listOpen]}\nCLOSED LIST: {[[item.id, item.idMap] for item in listClosed]}\nID MAP: {graphObject.dictNodes.idMap_}\n")
            #time.sleep(3)
            # This is the default behavior of dijkstra, no Death Pit node is calculate and by consecuence its not considered as a path in any case
            # NOTE: After checking again this code, i noticed this is redundant, it would be simpler just removing the pit listConnections like a 
            # wall node, but, i am not sure, since i want the dictNodes to be realistic this breaks this, since, its possible to go to this node but
            # not preferable, then this code suits well, i think?
            if type(node) is PitNode:
                listOpen.remove(node)
                continue
            
            # INFO: This methods loads the map (dictNodes) depending of the path, it solves a lot of things because now each path, if it has made changes 
            # to the map or position of the player, it has a unique map depending of where the bot goes and comes from
            graphObject.loadMap(node)
            
            # INFO: This function call loadUniqueConfig of the node but its handles diferent from createMap because its a unique config that its treated like
            # a temporary change in the map, not permanent like the bidirectional node, experimental, bugs are probable and more cases are needed to polish it
            graphObject.loadExternalConfigs(node)
            
            Count = Count + 1
            listConnections = node.listConnections
            nodeCost = node.costToReach
            nodeListPath = node.pathConnections
            
            debug_flag = False
            #if node.id == 38 and graphObject.dictNodes.idMap_ == 0:
            """if node.id == 78  and graphObject.dictNodes.idMap_ != 0:
                debug_flag = True
                print("DEBUG INIT", graphObject.dictNodes.idMap_, node.pathConnections)
            try:
                nodeT = graphObject.dictMaps[1][78]
                print("DEBUG INIT", nodeT, "PATH", nodeT.pathConnections)
            except:
                pass
            """
            for connection in listConnections:
                # INFO: Ignoring banned connections
                if connection.ban is True:
                    continue
                
                costToReach = connection.cost + nodeCost
                
                nextNode = graphObject.dictNodes[connection.toNode]
                
                nextNodeCost = nextNode.costToReach
                
                # INFO: To handle ice nodes we create temporary info and store it, the ice node is never added to the open list if it redirects, because 
                # we use this temporary info to reassign the variables as if we were in the ice node
                tmpNodeListPath = None
                if type(nextNode) is IceNode:
                    # INFO: The connection returned is a copy, trying to find it (in a list, ditc..) after dijkstra execution will fail
                    redirectConnection = nextNode.redirectsTo(pathNode=nodeListPath, connectionFrom=connection)
                    if redirectConnection:
                        tmpNodeListPath = Node.createTmpPath(pathNode=nodeListPath, connFrom=connection)
                        
                        connection = redirectConnection
                        
                        costToReach = connection.cost + costToReach
                        
                        nextNode = graphObject.dictNodes[connection.toNode]
                        
                        nextNodeCost = nextNode.costToReach
                
                if nextNodeCost is None:
                    if tmpNodeListPath:
                        nextNode.saveInfoPath(cost=costToReach, pathNode=tmpNodeListPath, connFrom=connection)
                    else:
                        nextNode.saveInfoPath(cost=costToReach, pathNode=nodeListPath, connFrom=connection)
                    
                    # INFO: Creating new map if changes must be made
                    if nextNode.confirmChanges() is True:
                        nextNode = graphObject.createMap(nextNode)
                    
                    listOpen.append(nextNode)
                else:
                    if costToReach >= nextNodeCost:
                        pass
                    elif costToReach < nextNodeCost:
                        nextNode.deletePathConnections()
                        
                        if tmpNodeListPath:
                            nextNode.saveInfoPath(cost=costToReach, pathNode=tmpNodeListPath, connFrom=connection)
                        else:
                            nextNode.saveInfoPath(cost=costToReach, pathNode=nodeListPath, connFrom=connection)
                        
                        cFlag = False
                        aFlag = False
                        
                        #
                        if nextNode.confirmChanges() is True:
                            nextNode = graphObject.createMap(nextNode)
                            listOpen.append(nextNode)
                            cFlag = True
                        
                        # INFO: If the costToReach is low that the actual nextNodeCost his data is only updated and we check if it has terminated checking 
                        # all his next nodes, if it has, we bring it back to the open list, if not, it means it havent been checked by the main loop
                        # It shouldn't be executed if nextNode.confirmChanges() was True
                        if nextNode in listClosed:
                            listClosed.remove(nextNode)
                            listOpen.append(nextNode)
                            aFlag = True
                        
                        if cFlag and aFlag:
                            raise ValueError("Something went wrong in dijkstra")
                    
            listOpen.remove(node)
            listClosed.append(node)
            debug_flag = False
    
    listFinal = list()
    goalNodesList = list()
    for idGoal in idsGoal:
        goalNodesList = [map[idGoal] for mapId, map in graphObject.dictMaps.items() if map[idGoal].costToReach is not None]
        for node in goalNodesList:
            listFinal.append(node)
    
    tmpList = [node for node in listFinal if node not in listClosed]
    for node in tmpList:
        listFinal.remove(node)
    
    #print("DEBUG INIT", idsGoal)
    #print("DEBUG INIT", listFinal)
    """
    for id, map in graphObject.dictMaps.items():
        print(11111111, map[78], map[78].pathConnections, "ID MAP", map.idMap_, id)
    """
    #print("OPEN LIST RE-ADDED NODES", listOpen.getreadded_())
    
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

# This is the pure algorithm, uses only one dictNodes/Map and it will not create new ones. Used to create possible connections of the skills
def pure_Dijkstra(dictNodes: dict, idsGoal: list, idStart: int, limit=None):
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
            Count = Count + 1
            listConnections = node.listConnections
            nodeCost = node.costToReach
            
            if limit is not None and nodeCost > limit:
                listOpen.remove(node)
                continue
                
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
    

# dijkstra will copy the dictNodes connections so the returned nodeGoal.pathConnections should not be trated as the same from the original dictNodes, this also means
# that the Nodes of original dictNodes doesnt have his dijkstra atributes with data, if you need to access to this processed info use pre_dijkstra, this is because the 
# following verifications modifies the nodes and since this function is going to be called more that one time not doing this could lead to create bad paths
def dijkstra(graphObject: Graph, idsGoal: list, idStart=None):
    if idStart is None:
        idStart = graphObject.userNode.id
        
    graphObjectCopy = copy.deepcopy(graphObject)
    dictNodesCopy = graphObjectCopy.dictNodes
    x = InfinityDetector()
    
    nodeGoal = pre_dijkstra(graphObjectCopy, idsGoal, idStart)
    
    # Ripper Precaution
    # Ripper is instakill, getting too close is game over, i dont know when it targets the player or any agent so i cant create a perfect strategy to avoid him, what i 
    # can do is at least avoid fall in one of his adyacent nodes, to do this i will check if the first connection of the pathConnections points to one of his 4 adyacent
    # nodes if it does we deleted the connections that points to this node, unless its the exit of a ryoIdGoal
    
    ripperNode = None
    for (id, node) in dictNodesCopy.items():
        if node.typeAgentIn == 4:
            ripperNode = node
        
    """
    if ripperNode is not None:
        while True:
            InfinityDetector.CountIter(x)
            nodeGoal = pre_dijkstra(graphObjectCopy, idsGoal, idStart)
            listRipperAdNodes = copy.deepcopy(ripperNode.idsRange1)
            listRipperAdNodes.extend(ripperNode.idsRange2indirect)
            print(listRipperAdNodes)
            idDeathNode = None
            firstConn = nodeGoal.pathConnections[0]
            
            if firstConn.toNode in listRipperAdNodes:
                idDeathNode = firstConn.toNode
            print("DEBUG INIT", idDeathNode)
            if idDeathNode is None:
                break
            else:
                firstConn.setBan(True)
    """
    
    # Casting skill precaution (Uses previous nodeGoal value generated)
    # If the objective is 1 cell away and a skill will be used to reach it, it will ban this connection skill so it doesnt use it and it uses the normal move
    # IMPROVE: To ban, the id of the skill is connection is used, and is added here, would be better to use the list passed from the strategy code, but how?,
    # problems or more likely the not execution of this code are in the future if the id's are changed
    
    if KEEPMOVESKILL:
        listIdMovementSkillsBan = [28, 8]
    else:
        listIdMovementSkillsBan = []
    
    if len(nodeGoal.pathConnections) == 1 and nodeGoal.pathConnections[0].idSkill in listIdMovementSkillsBan:
        nodeGoal.pathConnections[0].setBan(True)
        
        nodeGoal = pre_dijkstra(graphObjectCopy, idsGoal, idStart)
    
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
