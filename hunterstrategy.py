# Main Classes/Functions
from nodemap import Graph, Connection, PlayerNode, SliderNode, BidirectionalNode, dijkstra, pre_dijkstra, getMap

def strategyPath(jsonResponse):
    graphObject = Graph(jsonResponse)
    dictNodes = graphObject.dictNodes
    
    playerNode = graphObject.userNode
    enemyNode = graphObject.enemyNode
    ryoNode = graphObject.ryoNode
    kixNode = graphObject.kixNode
    ripperNode = graphObject.ripperNode
    listIdGoals = graphObject.listIdGoals
    
    # Hunter Codyfighters have more life and can tank attacks unlike Low life codyfighters (like Trickster) for this reason his movement must be different, my plan to this
    # bot is, prioritize the closest agent and attack him with everything, the exit is a option but should only chosse it if its really close
    
    # Goals Id
    # Dijkstra does the verification of which goal node is closest so we just need to add the id of the nodes close to ryo, kix and the enemy, which are the agents we
    # want to eliminate
    
    # If we get close to an agent his connection to our node gets deleted so using the listConnections of the agent doesnt work in this case, this is done by the Graph
    # with the purpose of creating a "logic" map of nodes but we can reverter it with the new function i added reverseDeleteAgentConnections()
    
    graphObject.reverseDeleteAgentConnections()
    
    for connection in ryoNode.listConnections:
        listIdGoals.append(connection.toNode)
    
    if kixNode is not None:
        for connection in kixNode.listConnections:
            listIdGoals.append(connection.toNode)
    
    for connection in enemyNode.listConnections:
        listIdGoals.append(connection.toNode)
    
    
    
    # And that should be all for now, "life awareness" is other think i want to add but i want to see first if it would help
    
    goalNode = dijkstra(dictNodes, playerNode.id, listIdGoals)
    
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
    
    hit_flag = False
    idHit = None
    skillPositionHit = None
    
    # In the case we have two targets we should prioritize some of the two so we dont attack differents targets in the same turn, i will prioritize kix since its more 
    # easy to eliminate second should be ryo and last the enemy
    
    # 2: Push  45: Hit
    for skill in listskills:
        if skill["id"] == 38 and skill["status"] == 1:
            directAttack_flag = True
            idDirectAttack = 38
            skillPositionDirectAttack = Count
            
        elif skill["id"] == 45 and skill["status"] == 1:
            hit_flag = True
            idHit = 45
            skillPositionHit = Count
        
        Count = Count + 1
        
    if directAttack_flag:
        listNodesToConnect = jsonResponse["players"]["bearer"]["skills"][skillPositionDirectAttack]["possible_targets"]
        
        for target in listNodesToConnect:
            objetiveCell = graphObject.getCell(target)
            objetiveNode = dictNodes[objetiveCell["id"]]
            # Here we check what nearby agents we want to attack, attacking llama is a no no
            listAgentsAttack = [1, 2, 200] # 1: Ryo  2: Kix  4: Ripper  200: Enemy
            listAgentsAvoid = [3, 5] # 3: Llama  5: Buzz
            customOrder = {2: 0, 1: 1, 200: 2}
            if objetiveNode.typeAgentIn in listAgentsAvoid:
                pass
            elif objetiveNode.typeAgentIn in listAgentsAttack :
                connection = Connection(cellFrom=playerNode.cell, cellTo=objetiveCell, cost=0, usedSkill=True, idSkill=idDirectAttack)
                listTargetsConnections.append(connection)
            else:
                print(f"UNKNOWN AGENT!! more info node: {objetiveNode} id: {objetiveNode.typeAgentIn}") 
        
        listTargetsConnections.sort(key=lambda connection: customOrder[dictNodes[connection.toNode].typeAgentIn])
    
    if hit_flag:
        listNodesToConnect = jsonResponse["players"]["bearer"]["skills"][skillPositionHit]["possible_targets"]
        
        for target in listNodesToConnect:
            objetiveCell = graphObject.getCell(target)
            objetiveNode = dictNodes[objetiveCell["id"]]
            listAgentsAttack = [1, 2, 200]
            listAgentsAvoid = [3, 5]
            customOrder = {2: 0, 1: 1, 200: 2}
            
            if objetiveNode.typeAgentIn in listAgentsAvoid:
                pass
            elif objetiveNode.typeAgentIn in listAgentsAttack :
                connection = Connection(cellFrom=playerNode.cell, cellTo=objetiveCell, cost=0, usedSkill=True, idSkill=idHit)
                listTargetsConnections.append(connection)
            else:
                print(f"UNKNOWN AGENT!! more info node: {objetiveNode} id: {objetiveNode.typeAgentIn}") 
        
        listTargetsConnections.sort(key=lambda connection: customOrder[dictNodes[connection.toNode].typeAgentIn])

    return listTargetsConnections
    