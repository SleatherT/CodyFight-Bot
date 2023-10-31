# This files saves the rules of how to attack like "modules" and is expected to be executed by a file in the root folder because of the imports
# Importing main Classes/Functions
from core.nodemap import Graph, AttackSKill
# User config 
from config import configAttack
# User config Variables
from config import listIdDamageSkills, idPrioritizedSkill, customOrder, listAgentsAttack, listAgentsAvoid

# Main function that decides what and how to attack depending of the config flags and values
def strategyAttack(jsonResponse):
    graphObject = Graph(jsonResponse)
    dictNodes = graphObject.dictNodes
    
    playerNode = graphObject.userNode
    enemyNode = graphObject.enemyNode
    
    listskills = graphObject.players["bearer"]["skills"]
    
    listTargetsConnections = list()
    dictSkills = dict()
    dictPrioritizedSkill = None
    
    Count = 0
    # Here we add the information of the skill we want to execute to a dictionary
    for skill in listskills:
        if skill["id"] in listIdDamageSkills and skill["status"] == 1:
            keyName = skill["name"]
            skillPosition = Count
            dictSkills[keyName] = {"skillPosition": skillPosition, "dictSkill": skill}
        
        # Here we choose a skill to prioritize, this will make the bot hoard energy to use this skill unless any skill would eliminate any nearby agent
        if skill["id"] == idPrioritizedSkill:
            dictPrioritizedSkill = skill
        
        Count = Count + 1
        
        
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
                connection = AttackSKill(nodeFrom=playerNode, nodeTo=objetiveNode, infoSkill=infoSkill["dictSkill"])
                listTargetsConnections.append(connection)
                
                listAgentsNearby.append(objetiveNode)
                
            else:
                print(f"UNKNOWN AGENT!! more info node: {objetiveNode} id: {objetiveNode.typeAgentIn}")
    
    # Checking if any avalible skill would kill any close agent, return the skillConnection if True
    if prioKill_flag is True:
        for skillConnection in listTargetsConnections:
            if skillConnection.killConfirmation is True:
                return [skillConnection]
    
    objetiveNode = None
    # Checking the agent with less life (if there is more of two agents to attack)
    if len(listAgentsNearby) > 1 and smartTargeting_flag:
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
            if dictNodes[skillConnection.toNode].typeAgentIn == objetiveNode.typeAgentIn:
                continue
            else:
                tmpList.append(skillConnection)
        
        for connection in tmpList:
            listTargetsConnections.remove(connection)
        
    elif len(listAgentsNearby) == 1 and smartTargeting_flag:
        objetiveNode = listAgentsNearby[0]
    else:
        pass

# Module prioKill_flag 
# Checks if any avalible skill would kill any close agent, return the skillConnection if True
def prioKill_function(confirmation_flag, listTargetsConnections):
    if confirmation_flag is True:
        for skillConnection in listTargetsConnections:
            if skillConnection.killConfirmation is True:
                return [skillConnection]