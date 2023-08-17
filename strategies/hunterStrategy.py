# Main Classes/Functions
from core.nodemap import Graph, Connection, PlayerNode, SliderNode, BidirectionalNode, dijkstra, pre_dijkstra, getMap

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
    # with the purpose of creating a "logic" map of nodes but we can reverse it with the new function i added reverseDeleteAgentConnections()
    
    graphObject.reverseDeleteAgentConnections()
    
    ryoTrapped_flag = graphObject.ryoTrapped_flag
    if ryoTrapped_flag:
        listIdGoals.append(graphObject.ryoIdGoal)
    
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
    dictSkills = dict()
    dictPrioritizedSkill = None
    
    # This dictionary is going to be used to organize the skill we want to use first, the key is the id of the skill and the value is the priority we want to give it
    # less the number = major priority. 
    customOrder = {27: 0,
                    3: 1,
                    38: 2,
                    45:3
                }
    
    # This list is used to define which skills to prioritize, if the bot has two or more of the prioritize skills it choose the first
    listPriorizedSkills = [27, 38]
    listPriorizedSkills.reverse()
    
    Count = 0
    # Here we add the information of the skill we want to execute to a dictionary
    for skill in listskills:
        # 2: Push  45: Hit  3: Magnetic Pull 27: Blade Strike
        if skill["id"] == 38 and skill["status"] == 1:
            keyName = "directAttack"
            idDirectAttack = 38
            skillPositionDirectAttack = Count
            dictSkills[keyName] = {"idSkill": idDirectAttack, "skillPosition": skillPositionDirectAttack, "damage": skill["damage"]}
            
        elif skill["id"] == 45 and skill["status"] == 1:
            keyName = "hit"
            idHit = 45
            skillPositionHit = Count
            dictSkills[keyName] = {"idSkill": idHit, "skillPosition": skillPositionHit, "damage": skill["damage"]}
        
        elif skill["id"] == 27 and skill["status"] == 1:
            keyName = "blade"
            idBlade = 27
            skillPositionBlade = Count
            dictSkills[keyName] = {"idSkill": idBlade, "skillPosition": skillPositionBlade, "damage": skill["damage"]}
        
        elif skill["id"] == 3 and skill["status"] == 1:
            keyName = "pull"
            idPull = 3
            skillPositionPull = Count
            dictSkills[keyName] = {"idSkill": idPull, "skillPosition": skillPositionPull, "damage": skill["damage"]}
        
        # Here we choose a skill to prioritize, this will make the bot hoard energy to use this skill unless any skill would eliminate any nearby agent
        if skill["id"] in listPriorizedSkills:
            dictPrioritizedSkill = skill
        
        Count = Count + 1
    
    # The rest of the code does the verifications, you dont need to add anything
    # Here we check what nearby agents we want to attack, attacking llama is a no no
    listAgentsAttack = [1, 2, 200] # 1: Ryo  2: Kix  4: Ripper  200: Enemy
    listAgentsAvoid = [3, 4, 5] # 3: Llama  5: Buzz
    
    listAgentsNearby = list()
    
    # We use the dictionary of skills to make a unique loop so we dont have to create code for each skill, just adding his info to the dictionary
    for (keyName, infoSkill) in dictSkills.items():
        listNodesToConnect = jsonResponse["players"]["bearer"]["skills"][infoSkill["skillPosition"]]["possible_targets"]
    
        for target in listNodesToConnect:
            objetiveCell = graphObject.getCell(target)
            objetiveNode = dictNodes[objetiveCell["id"]]
            
            if objetiveNode.typeAgentIn in listAgentsAvoid:
                pass
            elif objetiveNode.typeAgentIn in listAgentsAttack :
                connection = Connection(cellFrom=playerNode.cell, cellTo=objetiveCell, cost=0, usedSkill=True, idSkill=infoSkill["idSkill"])
                connection.setDamage(infoSkill["damage"])
                listTargetsConnections.append(connection)
                
                listAgentsNearby.append(objetiveNode)
                
            else:
                print(f"UNKNOWN AGENT!! more info node: {objetiveNode} id: {objetiveNode.typeAgentIn}")
    
    # Checking if any avalible skill would kill any close agent, return the skillConnection if True
    for skillConnection in listTargetsConnections:
        for agentNode in listAgentsNearby:
            if skillConnection.damage >= agentNode.totalLife:
                return [skillConnection]
    
    objetiveNode = None
    # Checking the agent with less life (if there is more of two agents to attack)
    if len(listAgentsNearby) > 1:
        minLife = None
        objetiveNode = None
        for agentNode in listAgentsNearby:
            if minLife is None:
                minLife = agentNode.totalLife
                objetiveNode = agentNode
                continue
            if agentNode.totalLife < minLife:
                minLife = agentNode.totalLife
                objetiveNode = agentNode
        
        # Removing the targets connections that doesnt point to this agent with less life
        tmpList = list()
        for skillConnection in listTargetsConnections:
            if dictNodes[skillConnection.toNode].typeAgentIn == agentNode.typeAgentIn:
                continue
            else:
                tmpList.append(skillConnection)
        
        for connection in tmpList:
            listTargetsConnections.remove(connection)
        
    elif len(listAgentsNearby) == 1:
        objetiveNode = listAgentsNearby[0]
    else:
        pass
    
    if objetiveNode is not None and dictPrioritizedSkill is not None:
        # Here we check if the prioritized skill is in cooldown or not
        if dictPrioritizedSkill["status"] == 1: # Status: 1 = Avalible tu use, -1 = Not enough energy to use, 0 = In cooldown
            for skillConnection in listTargetsConnections:
                if skillConnection.idSkill == dictPrioritizedSkill["id"]:
                    return [skillConnection]
        # If there is not energy to use it hoard energy so we reset the listTargetsConnections
        elif dictPrioritizedSkill["status"] == -1:
            listTargetsConnections = list()
        # If is in cooldown we check all the skills and we can use and calculate if at the end of the cooldown we are going to have enough energy to use it if we use
        # this skill if false we remove it
        elif dictPrioritizedSkill["status"] == 0:
            playerEnergy = jsonResponse["players"]["bearer"]["stats"]["energy"]
            tmpList = list()
            for skillConnection in listTargetsConnections:
                energyLeft = dictPrioritizedSkill["cost"] + playerEnergy - skillConnection.damage
                if energyLeft >= dictPrioritizedSkill["cost"]:
                    pass
                else:
                    tmpList.append(skillConnection)
            
            for skillConnection in tmpList:
                listTargetsConnections.remove(skillConnection)
    
    # Ordering the connections using the customOrder dict
    listTargetsConnections.sort(key=lambda connection: customOrder[connection.idSkill])


    return listTargetsConnections
    
