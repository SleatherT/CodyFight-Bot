from bots.hunterstrategy import strategyPath, strategyAttack
from core.nodemap import getMap, Graph
import json


fhandler = open("testmap.txt")
fhandler = fhandler.read()

jsonResponse = json.loads(fhandler)

print(getMap(jsonResponse))
graphObject = Graph(jsonResponse)
print("Player Node: ", graphObject.userNode)
nodeGoal = strategyPath(jsonResponse)
attack = strategyAttack(jsonResponse)
print("ATTACK CONNECTIONS: ", attack)
print("Node Goal: ", nodeGoal)
print("Path: ", nodeGoal.pathConnections)
print("Player Node: ", graphObject.userNode)
print("Reviewed Node: ", graphObject.dictNodes[0])
