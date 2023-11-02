# This files saves the rules of how to attack like "modules" and is expected to be executed by a file in the root folder because of the imports
# Importing main Classes/Functions
from core.nodemap import Graph, AttackSKill
# User config 
from config import configAttack
# User config Variables
from config import listIdDamageSkills, idPrioritizedSkill, customOrder, listAgentsAttack, listAgentsAvoid

# --MODULES--
# Each module is a function that its saved in a dict with his name as key and function as values. The name must be the same as the one in the config.py file
modulesDict = dict()

# prioritizeKill Module
# Returns the attack skill (connection) if any skill would kill any close agent, returns False otherwise 
# ARGUMENTS: listTargetsConnections, the list containing all the attack skills that the player can do

def prioritizeKill_function(listTargetsConnections):
    for skillConnection in listTargetsConnections:
        if skillConnection.killConfirmation is True:
            return [skillConnection]
    return False

modulesDict["prioritizeKill"] = prioKill_function

# smartTargeting Module
# Returns the closest enemy agent node with the lowest life, works well if there is two possible objectives like kix and the enemy
# ARGUMENTS: dictNodes, self-explanatory, the dict of nodes produced by the Graph class. listTargetsConnections, the list containing all the attack skills 
# that the player can do. listAgentsNearby, a list containing the nodes of the agents that are possible to attack by consecuence is a list containing the 
# closest enemy agents

# TEST IF THE CONNECTIONS OF THE LIST OF TARGETS ARE REMOVED IN PLACE

# INFO: This function has potential to do a lot of things and can be improved a lot like targeting the lowest enemy agent in the entire map but for this 
# it should get information from strategyPath()
def smartTargeting_function(dictNodes, listTargetsConnections, listAgentsNearby)
    objetiveNode = None
    if len(listAgentsNearby) > 1:
        minLife = None
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
        
    elif len(listAgentsNearby) == 1:
        objetiveNode = listAgentsNearby[0]
    else:
        pass
    
    return objetiveNode

modulesDict["smartTargeting"] = smartTargeting_function

# prioritizeSkill Module
# Returns the skill if its available (status 1, which doesn't mean that it can be used, this must be fixed!!)
def prioritizeSkill():
    
    
    if objetiveNode is not None and dictPrioritizedSkill is not None:
        # Here we check if the prioritized skill is in cooldown or not
        if dictPrioritizedSkill["status"] == 1: # Status: 1 = Avalible tu use, -1 = Not enough energy to use, 0 = In cooldown
            for skillConnection in listTargetsConnections:
                if skillConnection.idSkill == dictPrioritizedSkill["id"]:
                    return [skillConnection] # FIX: Returning right away the prioritized skill is okay if its possible to use always (if it has a big range), otherwise...
        # If there is not energy to use it hoard energy so we reset the listTargetsConnections
        elif dictPrioritizedSkill["status"] == -1:
            listTargetsConnections = list()
        # If is in cooldown we check all the skills and we can use and calculate if at the end of the cooldown we are going to have enough energy to use it if we use
        # this skill if false we remove it
        elif dictPrioritizedSkill["status"] == 0:
            playerEnergy = jsonResponse["players"]["bearer"]["stats"]["energy"]
            tmpList = list()
            for skillConnection in listTargetsConnections:
                energyLeft = dictPrioritizedSkill["cost"] + playerEnergy - skillConnection.castCost
                if energyLeft >= dictPrioritizedSkill["cost"]:
                    pass
                else:
                    tmpList.append(skillConnection)
            
            for skillConnection in tmpList:
                listTargetsConnections.remove(skillConnection)

# --MAIN FUNCTION--
# This function executes the modules depending of the config flags and values
def strategyAttack(jsonResponse):
    graphObject = Graph(jsonResponse)
    dictNodes = graphObject.dictNodes
    
    playerNode = graphObject.userNode
    enemyNode = graphObject.enemyNode
    
    listskills = graphObject.players["bearer"]["skills"]
    
    listTargetsConnections = list()
    listAgentsNearby = list()
    dictPrioritizedSkill = None
    
    dictSkills = dict()
    
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
    
    objetiveNode = None
    
    #__Modules Execution__
    
    configAttack = dict(sorted(configAttack.items()))
    for (order, skillConfig) in configAttack.items():
        skillName = skillConfig["name"]
        skillFunction = modulesDict[skillName]
        skillFunction()
    
    
    
    

