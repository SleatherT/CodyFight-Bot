from pathfinding2 import Graph, dijkstra, bidirectionalCheck

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
    