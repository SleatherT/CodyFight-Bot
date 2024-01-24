# Main Classes/Functions
from core.nodemap import Graph, Connection, PlayerNode, SliderNode, BidirectionalNode, dijkstra, pre_dijkstra, getMap

def strategyPath(jsonResponse):
    graphObject = Graph(jsonResponse)
    dictNodes = graphObject.dictNodes
    
    playerNode = graphObject.userNode
    enemyNode = graphObject.enemyNode
    ryoNode = graphObject.ryoNode
    ripperNode = graphObject.ripperNode
    listIdGoals = graphObject.listIdGoals
    
    swapSkill_flag = False
    listskills = graphObject.players["bearer"]["skills"]
    for skill in listskills:
        if skill["id"] == 5 and skill["status"] == 1:
            swapSkill_flag = True
            idSwapSkill = 5
    
    # My strategy for this bot is focused on reaching the exit so we are going to use swap skill but if its not possible trapping ryo is another option, killing an enemy with 
    # a preseason trickster is something hard so it will only do this if its low life and the enemy has no skills to attack, in case ryo is not close to be trapped,
    # it should try killing the enemy with the condition i said early, if is close to be trapped it should go to his adyacent node, if this tree ways of winning are not true
    # it should chosse a node far from the enemy and other dangerous agents
    
    # Goals id
    # The Goals id depend of your strategy, if you want to kill a enemy use his adyacent nodes ids as the nodes you want to reach, same for ryo. The graph has 
    # already made the verification if ryo is close to be trapped (sorrounded by an agent/enemy and with only one movement), so you just need to access to the flag and id
    # of the node you need to reach to win
    
    ryoIsObjetive_flag = False
    exitActive_flag = False
    ryoTrapped_flag = graphObject.ryoTrapped_flag
    if len(listIdGoals) > 0:
        exitActive_flag = True
    elif len(listIdGoals) == 0:
        ryoIsObjetive_flag = True
        for connection in ryoNode.listConnections:
            listIdGoals.append(connection.toNode)
            ryoIsObjetive_flag = True
    elif ryoTrapped_flag:
        listIdGoals.append(graphObject.ryoIdGoal)
        ryoIsObjetive_flag = True
    
    # Skill Targets
    # To be able to use the skills, we create a connection between the player and the target and setting to True the usedSkill property
    listNodesToConnect = jsonResponse["players"]["bearer"]["skills"][0]["possible_targets"]
    if swapSkill_flag:
        for position in listNodesToConnect:
            objetiveCell = graphObject.getCell(position)
            connection = Connection(cellFrom=playerNode.cell, cellTo=objetiveCell, cost=0, usedSkill=True, idSkill=idSwapSkill)
            playerNode.listConnections.append(connection)
    
    # Swap Pseudo-Connections
    # To give the ability of taking into account the possibility of bypassing agents to the bot we should add connections from the cells we can probably target an agent,
    # in this way he could "see" a possible path, to do this the range of the skill is used, the range is how much connections can bypass, thats why the max range of swap
    # is 2 cells if we are aligned in a straight line, we use pre_dijkstra (dijkstra doesnt add info to the nodes in any way because uses a copy of the dictNodes
    # pre_dijkstra do this) and take the nodes less or equal of 2 cost
    # First Problem (Solved): The spreading proccess using the normal dictNodes does work for this because the invalid nodes doesnt have connections so if an agent 
    # is reachable crossing walls, this will not work, we are going to need a pure dictNodes 
    dictNodesPure = graphObject.dictNodesPure
    listIdAgents = graphObject.listIdAgents
    if swapSkill_flag:
        listIdAlmostFullAgents = list(listIdAgents)
        listIdAlmostFullAgents.append(enemyNode.id)
        for id in listIdAlmostFullAgents:
            pre_dijkstra(dictNodesPure, id, [], True)
            agentNode = dictNodesPure[id]
        
            listPseudoNodes = list()
            for (id, node) in dictNodesPure.items():
                cost = node.costToReach
                usedSliderNode_flag = False
                usedBiNode_flag = False
                # The agent node has cost 0 and since we are creating connections to him we ignore him
                if cost == 0:
                    continue
                if cost <= 2:
                    # We need to check if the pathConnections of the node didnt used a slider or bidirectional tile, if we dont check it would create impossible connections
                    for connection in node.pathConnections:
                        nextNode = dictNodesPure[connection.toNode]
                        if type(nextNode) is SliderNode and nextNode.isCharged is True:
                            usedSliderNode_flag = True
                        if type(nextNode) is BidirectionalNode and nextNode.isCharged is True:
                            usedBiNode_flag = True
                    if usedSliderNode_flag is False and usedBiNode_flag is False:
                        listPseudoNodes.append(node)
            for node in listPseudoNodes:
                if node.typeAgentIn is not None:
                    continue
                if node.typeNode in [1, 3, 17, 12]:
                    continue
                connection = Connection(cellFrom=node.cell, cellTo=agentNode.cell, cost=0, usedSkill=True, idSkill=idSwapSkill)
                nodeFromRealDictNodes = dictNodes[node.id]
                nodeFromRealDictNodes.listConnections.append(connection)
    
    # Buzz/Ryo Fix
    # This is probably the most important part of the swap skill and is a fix, if there is no exit in the map and ryo is close to be trapped, the objective is the ryoIdGoal
    # and it will use any agent that is trapping Ryo (Buzz most likely but the ryo itself too), to reach his goal, which is contraproducent. To solve this if the objective 
    # is Ryo we can use this info to ban the use of the skill connections that use the agents blocking the way of Ryo and Ryo too
    # To achive this i have added a new property to the connections object called "ban", this property is used in the dijkstra algorithm, if its True it shouldn't be proccesed
    # with this we dont need to delete this connections
    if ryoIsObjetive_flag:
        listIdAgentsSorrounding = graphObject.listIdAgentsSorrounding
        listNoSwap = listIdAgentsSorrounding + [ryoNode.id]
        for (id, node) in dictNodes.items():
            for connection in node.listConnections:
                if connection.toNode in listNoSwap and connection.usedSkill is True and connection.idSkill == idSwapSkill:
                    connection.setBan(True)
    
    goalNode = dijkstra(dictNodes, playerNode.id, listIdGoals, ignoreLandmines=False)
    
    return goalNode
    
# Function separated from strategyPath, strategyPath should be only used to reach certain objective while this function decides what agent attack
def strategyAttack(jsonResponse):
    graphObject = Graph(jsonResponse)
    dictNodes = graphObject.dictNodes
    
    playerNode = graphObject.userNode
    enemyNode = graphObject.enemyNode
    
    listskills = graphObject.players["bearer"]["skills"]
    
    listTargetsConnections = list()
    
    directAttack_flag = False
    idDirectAttack = None
    Count = 0
    skillPositionDirectAttack = None
    for skill in listskills:
        if skill["id"] == 38 and skill["status"] == 1:
            directAttack_flag = True
            idDirectAttack = 38
            skillPositionDirectAttack = Count
        Count = Count + 1
            
    if directAttack_flag:
        listNodesToConnect = jsonResponse["players"]["bearer"]["skills"][skillPositionDirectAttack]["possible_targets"]
        
        for target in listNodesToConnect:
            objetiveCell = graphObject.getCell(target)
            objetiveNode = dictNodes[objetiveCell["id"]]
            # Here we check what nearby agents we want to attack, attacking llama is a no no
            listAgentsAttack = [1, 2, 4, 200] # 1: Ryo  2: Kix  4: Ripper  200: Enemy
            listAgentsAvoid = [3, 5] # 3: Llama  5: Buzz
            if objetiveNode.typeAgentIn in listAgentsAvoid:
                pass
            elif objetiveNode.typeAgentIn in listAgentsAttack :
                connection = Connection(cellFrom=playerNode.cell, cellTo=objetiveCell, cost=0, usedSkill=True, idSkill=idDirectAttack)
                listTargetsConnections.append(connection)
            else:
                print(f"UNKNOWN AGENT!! more info node: {objetiveNode} id: {objetiveNode.typeAgentIn}") 
    
    return listTargetsConnections
    
