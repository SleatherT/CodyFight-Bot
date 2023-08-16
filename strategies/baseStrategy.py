from core.nodemap import Graph, dijkstra

# This function is the core of the bot, use all the information of the graph, node and connections to create the strategy that the bot will follow
# This is also an example of a basic bot that simply moves towards the exit (cell type 2), if there is no exit moves close to ryo
def strategyPath(jsonResponse):
    graphObject = Graph(jsonResponse)
    dictNodes = graphObject.dictNodes
    
    playerNodeId = graphObject.userNode.id
    ryoNode = graphObject.ryoNode
    listIdGoals = graphObject.listIdGoals
    
    if len(listIdGoals) > 0:
        pass
    else:
        for connection in ryoNode.listConnections:
            listIdGoals.append(connection.toNode)
    
    goalNode = dijkstra(dictNodes, playerNodeId, listIdGoals)
    
    return goalNode
    
def strategyAttack(jsonResponse):
    graphObject = Graph(jsonResponse)
    dictNodes = graphObject.dictNodes
    
    playerNode = graphObject.userNode
    enemyNode = graphObject.enemyNode
    
    listskills = graphObject.players["bearer"]["skills"]
    
    listTargetsConnections = list()
    
    push_flag = False
    idPush = None
    Count = 0
    skillPositionPush = None
    for skill in listskills:
        if skill["id"] == 2 and skill["status"] == 1:
            push_flag = True
            idPush = 2
            skillPositionPush = Count
        Count = Count + 1
            
    if push_flag:
        listNodesToConnect = jsonResponse["players"]["bearer"]["skills"][skillPositionPush]["possible_targets"]
        
        for target in listNodesToConnect:
            objetiveCell = graphObject.getCell(target)
            objetiveNode = dictNodes[objetiveCell["id"]]
            # Here we check what nearby agents we want to attack
            listAgentsAttack = [1, 2, 4, 200] # 1: Ryo  2: Kix  4: Ripper  200: Enemy
            listAgentsAvoid = [3, 5] # 3: Llama  5: Buzz
            if objetiveNode.typeAgentIn in listAgentsAvoid:
                pass
            elif objetiveNode.typeAgentIn in listAgentsAttack :
                connection = Connection(cellFrom=playerNode.cell, cellTo=objetiveCell, cost=0, usedSkill=True, idSkill=idPush)
                listTargetsConnections.append(connection)
    
    return listTargetsConnections