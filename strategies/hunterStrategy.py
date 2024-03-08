# Main Classes/Functions
from config import GO_EXIT, GO_TELEPORT, DEFAULT_TARGETS, FALLBACK_TO_DEFAULT, GO_ENEMY, GO_RYO, GO_KIX, GO_RIPPER, GO_LLAMA, GO_BUZZ, GO_RYO_SURROUNDED, DEFAULT_ATTACK, ATTACK_ENEMY, ATTACK_RYO, ATTACK_KIX, ATTACK_LLAMA, ATTACK_RIPPER, ATTACK_BUZZ, BLOCK_NATIVE, RANDOM_CAST_SKILLS
from core.nodemap import Node, Graph, Connection, AttackSKill, MovementSkill, PlayerNode, EnemyNode, SliderNode, SpecialTileNode, BidirectionalNode, TrapNode, SentryNode, dijkstra, pre_dijkstra, getMap, pure_Dijkstra
import time
import copy
from itertools import combinations

def strategyPath(jsonResponse):
    graphObject = Graph(jsonResponse)
    dictNodes = graphObject.dictNodes
    
    playerNode = graphObject.userNode
    enemyNode = graphObject.enemyNode
    ryoNode = graphObject.ryoNode
    kixNode = graphObject.kixNode
    ripperNode = graphObject.ripperNode
    buzzNode = graphObject.buzzNode
    listIdGoalsGraph = graphObject.listIdGoals
    llamaNode = graphObject.llamaNode
    
    # Hunter Codyfighters have more life and can tank attacks unlike Low life codyfighters (like Trickster) for this reason his movement must be different, my plan to this
    # bot is, prioritize the closest agent and attack him with everything, the exit is a option but should only chosse it if its really close
    
    # Goals Id
    # Dijkstra does the verification of which goal node is closest so we just need to add the id of the nodes close to ryo, kix and the enemy, which are the agents we
    # want to eliminate, we use the .idsRange1 property of the Nodes for this
    
    customOptions = [GO_EXIT, GO_TELEPORT, GO_ENEMY, GO_RYO, GO_KIX, GO_RIPPER, GO_LLAMA, GO_RYO_SURROUNDED]
    
    listIdGoals = list()
    default_flag = False
    if DEFAULT_TARGETS is True and True not in customOptions:
        if graphObject.ryoTrapped_flag:
            listIdGoals.append(graphObject.ryoIdGoal)
            
        if kixNode is not None:
            listIdGoals.extend(kixNode.idsRange1)
        
        listIdGoals.extend(enemyNode.idsRange1)
        
        listIdGoals.extend(listIdGoalsGraph)
        
        default_flag = True
    
    if GO_ENEMY is True and default_flag is False:
        listIdGoals.extend(enemyNode.idsRange1)
    if GO_RYO is True and ryoNode is not None and default_flag is False:
        listIdGoals.extend(ryoNode.idsRange1)
    if GO_KIX is True and kixNode is not None and default_flag is False:
        listIdGoals.extend(kixNode.idsRange1)
    if GO_LLAMA is True and llamaNode is not None and default_flag is False:
        listIdGoals.extend(llamaNode.idsRange1)
    if GO_RIPPER is True and ripperNode is not None and default_flag is False:
        listIdGoals.extend(ripperNode.idsRange1)
    if GO_BUZZ is True and buzzNode is not None and default_flag is False:
        listIdGoals.extend(buzzNode.idsRange1)
    
    if GO_RYO_SURROUNDED is True and ryoNode is not None and default_flag is False:
        if graphObject.ryoTrapped_flag:
            listIdGoals.append(graphObject.ryoIdGoal)
    if GO_EXIT is True and default_flag is False:
        listIdGoals.extend(listIdGoalsGraph)
    if GO_TELEPORT is True and len(graphObject.listConnectionsBidirectionals) > 0 and default_flag is False:
        listIdGoals.append(graphObject.listConnectionsBidirectionals[0].fromNode)
        listIdGoals.append(graphObject.listConnectionsBidirectionals[0].toNode)
    
    if FALLBACK_TO_DEFAULT is True and len(listIdGoals) == 0:
        if graphObject.ryoTrapped_flag:
            listIdGoals.append(graphObject.ryoIdGoal)
        if kixNode is not None:
            listIdGoals.extend(kixNode.idsRange1)
        listIdGoals.extend(enemyNode.idsRange1)
        listIdGoals.extend(listIdGoalsGraph)
    
    # Movement Skills 
    # (Just adding the movements of the skill with cost 0 to the player node should prioritize the use of these by dijkstra)
    
    # Add Here the id of the skills
    listIdMovementSkills = [28, 8] # 28: Double Time  8: Run run run
    
    # If any movement skill is available to use, it will use it, no restrictions of energy for now
    
    listskills = graphObject.players["bearer"]["skills"]
    for skill in listskills:
        if skill["id"] in listIdMovementSkills and skill["status"] == 1:
            skillObjectives = skill["possible_targets"]
            
            for nextCellCoord in skillObjectives:
                nextCell = graphObject.getCell(nextCellCoord)
                nextNode = graphObject.getNode(nextCell["id"])
                connection = MovementSkill(nodeFrom=playerNode, nodeTo=nextNode, infoSkill=skill, cost=0)
                playerNode.listConnections.append(connection)
    
    # And that should be all for now, "life awareness" is other think i want to add but i want to see first if it would help
    
    goalNode = dijkstra(graphObject, listIdGoals, playerNode.id)
    
    return goalNode
    
# Function separated from strategyPath, strategyPath should be only used to reach certain objective while this function decides what agent attack
def strategyAttackDamage(jsonResponse):
    graphObject = Graph(jsonResponse)
    dictNodes = graphObject.dictNodes
    
    playerNode = graphObject.userNode
    enemyNode = graphObject.enemyNode
    llamaNode = graphObject.llamaNode
    
    listskills = graphObject.players["bearer"]["skills"]
    
    listAgentAttacks = list()
    listTrapAttacks = list()
    dictSkillsPure = dict()
    dictPrioritizedSkill = None
    
    # Experimental Code
    # INFO: Automatically saves the skills with damage, i am not sure if all the skills that have the damage atribute > 0, are always casted over enemies, in the
    # case some arent, like casting buildings that at the same time does damage, well, some parts of this code cant handle that, i think so?
    
    Count = 0
    for skill in listskills:
        if skill["damage"] > 0:
            dictSkillsPure[skill["name"]] = {"skillPosition": Count, "dictSkill": skill}
        if BLOCK_NATIVE is True and skill["damage"] > 0 and skill["is_native"] is True:
            del dictSkillsPure[skill["name"]]
        Count = Count + 1
    
    maxDamage = None
    # The prioritized skill will be the native skill, if its an attack skill of course, otherwise will be the one with more damage
    # The dictPrioritizedSkill is always present regardless of his status
    for (key, skill["dictSkill"]) in dictSkillsPure.items():
        isNative = skill["is_native"]
        skillDamage = skill["damage"]
        if isNative is True:
            dictPrioritizedSkill = skill
            break
        elif maxDamage is None:
            maxDamage = skillDamage
            dictPrioritizedSkill = skill
        elif maxDamage > skillDamage:
            maxDamage = skillDamage
            dictPrioritizedSkill = skill
    
    # The order of the skills to execute is by default the one with more damage first
    for n in range(len(dictSkillsPure)):
        customOrder = {v["dictSkill"]["id"]: n for k, v in sorted(dictSkillsPure.items(), key=lambda skill: skill[1]["dictSkill"]["damage"])}
    
    # Taking only the active skills with targets
    dictSkills = {k: v for k, v in dictSkillsPure.items() if v["dictSkill"]["status"] == 1}
    """
    if llamaNode is not None:
        llamaTotalLife = llamaNode.totalLife
        selectedSkills = {keyName: skillInfo for keyName, skillInfo in dictSkillsPure.items() if llamaTotalLife - skillInfo["dictSkill"]["damage"] > 0}
        skillsCombined = list(combinations(selectedSkills.items(), 2))
        
        validCombos = dict()
        validCombos["Actives"] = list()
        validCombos["Inactives"] = list()
        for combo in skillsCombined:
            if llamaTotalLife - (combo[0][1]["dictSkill"]["damage"] + combo[1][1]["dictSkill"]["damage"]) <= 0:
                if combo[0][1]["dictSkill"]["status"] == 1 and combo[1][1]["dictSkill"]["status"] == 1:
                    validCombos["Actives"].append({combo[0][0]: combo[0][1], combo[1][0]: combo[1][1]})
                else:
                    validCombos["Inactives"].append({combo[0][0]: combo[0][1], combo[1][0]: combo[1][1]})
        
        if len(validCombos["Actives"]) >= 1:
            dictSkills = validCombos["Actives"][0]
        # If we need only energy to cast the combo we wait = return a empy list
        elif len(validCombos["Inactives"]) >= 1:
            return []
    """
    # Here we check what nearby agents we want to attack
    # 1: Ryo  2: Kix  3: Llama  4: Ripper 5: Buzz  100: Player  200: Enemy
    customOptions = [ATTACK_ENEMY, ATTACK_RYO, ATTACK_KIX, ATTACK_LLAMA, ATTACK_RIPPER, ATTACK_BUZZ]
    dictOptions = [{ATTACK_ENEMY: 200}, {ATTACK_RYO: 1}, {ATTACK_KIX: 2}, {ATTACK_LLAMA: 3}, {ATTACK_RIPPER: 4}, {ATTACK_BUZZ: 5}]
    
    listIdAgentsAttack = list()
    listAgentsAvoid = [1, 2, 3, 4, 5, 100, 200]
    
    if DEFAULT_ATTACK is True and True not in customOptions:
        listIdAgentsAttack.extend([2, 200])
        listAgentsAvoid.remove(2)
        listAgentsAvoid.remove(200)
    else:
        for dictOption in dictOptions:
            for flag, idAgent in dictOption.items():
                if flag is True:
                    listIdAgentsAttack.append(idAgent)
                    listAgentsAvoid.remove(idAgent)
    
    listAgentsNearby = list()
    
    # We use the dictionary of skills to make a unique loop so we dont have to create code for each skill, just adding his info to the dictionary
    for (keyName, infoSkill) in dictSkills.items():
        listNodesToConnect = jsonResponse["players"]["bearer"]["skills"][infoSkill["skillPosition"]]["possible_targets"]
    
        for target in listNodesToConnect:
            objetiveCell = graphObject.getCell(target)
            objetiveNode = dictNodes[objetiveCell["id"]]
            
            if objetiveNode.typeAgentIn in listAgentsAvoid:
                pass
            elif objetiveNode.typeAgentIn in listIdAgentsAttack :
                connection = AttackSKill(nodeFrom=playerNode, nodeTo=objetiveNode, infoSkill=infoSkill["dictSkill"])
                listAgentAttacks.append(connection)
                
                listAgentsNearby.append(objetiveNode)
            elif type(objetiveNode) is TrapNode:
                connection = AttackSKill(nodeFrom=playerNode, nodeTo=objetiveNode, infoSkill=infoSkill["dictSkill"])
                # No Strategy
                listTrapAttacks.append(connection)
            elif type(objetiveNode) is SentryNode:
                connection = AttackSKill(nodeFrom=playerNode, nodeTo=objetiveNode, infoSkill=infoSkill["dictSkill"])
                # IMPROVE: Temporary adding attacks against Sentry Turrets to the listAgentAttacks until the creation of a strategy for this objective 
                listAgentAttacks.append(connection)
            else:
                print(f"UNKNOWN AGENT OR TILE TO ATTACK!! more info node: {objetiveNode} id agent: {objetiveNode.typeAgentIn}, id node: {objetiveNode.typeNode}, skill: {keyName}")
    
    # Checking if any avalible skill would kill any close agent, return the skillConnection if True
    for skillConnection in listAgentAttacks:
        if skillConnection.killConfirmation is True:
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
        for skillConnection in listAgentAttacks:
            if dictNodes[skillConnection.toNode].typeAgentIn == objetiveNode.typeAgentIn:
                continue
            else:
                tmpList.append(skillConnection)
        
        for connection in tmpList:
            listAgentAttacks.remove(connection)
        
    elif len(listAgentsNearby) == 1:
        objetiveNode = listAgentsNearby[0]
    else:
        pass
    
    if objetiveNode is not None and dictPrioritizedSkill is not None:
        # Here we check if the prioritized skill is in cooldown or not
        if dictPrioritizedSkill["status"] == 1: # Status: 1 = Avalible tu use, -1 = Not enough energy to use, 0 = In cooldown
            for skillConnection in listAgentAttacks:
                if skillConnection.idSkill == dictPrioritizedSkill["id"]:
                    return [skillConnection] # FIX: Returning right away the prioritized skill is okay if its possible to use always (if it has a big range), otherwise...
        # If there is not energy to use it hoard energy so we reset the listAgentAttacks
        elif dictPrioritizedSkill["status"] == -1:
            listAgentAttacks = list()
        # If is in cooldown we check all the skills and we can use and calculate if at the end of the cooldown we are going to have enough energy to use it if we use
        # this skill if false we remove it
        elif dictPrioritizedSkill["status"] == 0:
            playerEnergy = jsonResponse["players"]["bearer"]["stats"]["energy"]
            tmpList = list()
            for skillConnection in listAgentAttacks:
                energyLeft = dictPrioritizedSkill["cost"] + playerEnergy - skillConnection.castCost
                if energyLeft >= dictPrioritizedSkill["cost"]:
                    pass
                else:
                    tmpList.append(skillConnection)
            
            for skillConnection in tmpList:
                listAgentAttacks.remove(skillConnection)
    
    # Ordering the connections using the customOrder dict
    listAgentAttacks.sort(key=lambda connection: customOrder[connection.idSkill])

    return listAgentAttacks


def strategySkills(jsonResponse):
    graphObject = Graph(jsonResponse)
    dictNodes = graphObject.dictNodes
    
    playerNode = graphObject.userNode
    enemyNode = graphObject.enemyNode
    
    listskills = graphObject.players["bearer"]["skills"]
    
    dictSkills = dict()
    Count = 0
    
    # Add here the id of the skills
    listIdSkills = []
    listIdObjectivesTiles = []
    
    # # 1: Ryo  2: Kix  3: Llama  4: Ripper 5: Buzz  100: Player  200: Enemy
    listIdObjectivesAgents = []
    
    for skill in listskills:
        if skill["id"] in listIdSkills and skill["status"] == 1:
            dictSkills[skill["name"]] = {"skillPosition": Count, "dictSkill": skill}
        elif RANDOM_CAST_SKILLS and skill["status"] == 1:
            dictSkills[skill["name"]] = {"skillPosition": Count, "dictSkill": skill}
        Count = Count + 1
    
    listSkills = list() 
    for (keyName, infoSkill) in dictSkills.items():
        listNodesToConnect = jsonResponse["players"]["bearer"]["skills"][infoSkill["skillPosition"]]["possible_targets"]
    
        for target in listNodesToConnect:
            objetiveCell = graphObject.getCell(target)
            objetiveNode = dictNodes[objetiveCell["id"]]
            if objetiveNode.typeNode in listIdObjectivesTiles:
                connection = AttackSKill(nodeFrom=playerNode, nodeTo=objetiveNode, infoSkill=infoSkill["dictSkill"])
                listSkills.append(connection)
            elif objetiveNode.typeAgentIn in listIdObjectivesAgents:
                connection = AttackSKill(nodeFrom=playerNode, nodeTo=objetiveNode, infoSkill=infoSkill["dictSkill"])
                listSkills.append(connection)
            elif RANDOM_CAST_SKILLS:
                connection = AttackSKill(nodeFrom=playerNode, nodeTo=objetiveNode, infoSkill=infoSkill["dictSkill"])
                listSkills.append(connection)
            else:
                print(f"UNKNOWN AGENT OR TILE TO ATTACK!! more info node: {objetiveNode} id agent: {objetiveNode.typeAgentIn}, id node: {objetiveNode.typeNode}, skill: {keyName}")
    
    
    return listSkills

INVERSE_SKILLS = False
def strategyAttack(jsonResponse):
    if INVERSE_SKILLS:
        listSkills = strategyAttackDamage(jsonResponse)
        listSkills.extend(strategySkills(jsonResponse))
    else:
        listSkills = strategySkills(jsonResponse)
        listSkills.extend(strategyAttackDamage(jsonResponse))
    
    return listSkills

# Special Strategies

def specialStrategyAttack(jsonResponse, strategyPathInfo):
    #print("DEBUG INIT", strategyPathInfo)
    if strategyPathInfo["confirmation"] is False:
        return []
    
    graphObject = Graph(jsonResponse)
    dictNodes = graphObject.dictNodes
    
    playerNode = graphObject.userNode
    enemyNode = graphObject.enemyNode
    
    listskills = graphObject.players["bearer"]["skills"]
    
    dictSkills = dict()
    Count = 0
    # 60: Reel  30: Fried pray
    skillsId = [30, 60]
    friedPrayDict = None
    for skill in listskills:
        if skill["id"] in skillsId and skill["status"] == 1:
            dictSkills[skill["name"]] = {"skillPosition": Count, "dictSkill": skill}
        if skill["id"] == 30:
            friedPrayDict = skill
        Count = Count + 1
    
    listSkills = list() 
    friedAttack = []
    reelAttack = []
    for (keyName, infoSkill) in dictSkills.items():
        listNodesToConnect = jsonResponse["players"]["bearer"]["skills"][infoSkill["skillPosition"]]["possible_targets"]
        #print("DEBUG INIT", keyName)
        #print("DEBUG INIT", strategyPathInfo["goalNode"].notes[1].fromNode)
        
        for target in listNodesToConnect:
            objetiveCell = graphObject.getCell(target)
            objetiveNode = dictNodes[objetiveCell["id"]]
            
            if infoSkill["dictSkill"]["id"] == 30 and objetiveNode.id == strategyPathInfo["goalNode"].notes[1].fromNode:
                friedAttack.append(AttackSKill(nodeFrom=playerNode, nodeTo=objetiveNode, infoSkill=infoSkill["dictSkill"]))
            elif infoSkill["dictSkill"]["id"] == 60 and type(objetiveNode) is EnemyNode:
                reelAttack.append(AttackSKill(nodeFrom=playerNode, nodeTo=objetiveNode, infoSkill=infoSkill["dictSkill"]))
            else:
                print(f"UNKNOWN AGENT OR TILE TO ATTACK!! more info node: {objetiveNode} id agent: {objetiveNode.typeAgentIn}, id node: {objetiveNode.typeNode}, skill: {keyName}")
    #print("DEBUG INIT: friedAttack", friedAttack)
    #print("DEBUG INIT: reelAttack", reelAttack)
    if len(friedAttack) > 0 and len(reelAttack):
        return friedAttack
    
    # In cooldown
    if friedPrayDict is not None and friedPrayDict["status"] == 0:
        if len(reelAttack) > 0:
            return reelAttack
    
    return listSkills
    
def specialStrategyPath(jsonResponse):
    graphObject = Graph(jsonResponse)
    dictNodes = graphObject.dictNodes
    
    playerNode = graphObject.userNode
    enemyNode = graphObject.enemyNode
    ryoNode = graphObject.ryoNode
    kixNode = graphObject.kixNode
    ripperNode = graphObject.ripperNode
    listIdGoals = graphObject.listIdGoals
    
    listIdGoals = list()
    
    copyGraph = copy.deepcopy(graphObject)
    
    #print("DEBUG INIT", enemyNode.idsRange2directSemiClear)
    
    # Creating connections from the enemy node
    pure_Dijkstra(copyGraph.dictNodesPure, [], enemyNode.id)
    #print("DEBUG INIT: PURE ENEMY NODE", copyGraph.dictNodesPure[enemyNode.id])
    selectedNodesList = list()
    for id, node in copyGraph.dictNodesPure.items():
        if node.costToReach == 2:
            selectedNodesList.append(node)
    
    tmpList = list()
    for node in selectedNodesList:
        previousDirection = None
        for connection in node.pathConnections:
            currentDirection = connection.direction
            if previousDirection is None:
                previousDirection = currentDirection
            else:
                if currentDirection == previousDirection and type(graphObject.dictNodesPure[connection.fromNode]) is Node:
                #if currentDirection == previousDirection:
                    pass
                elif currentDirection == previousDirection and graphObject.dictNodesPure[connection.fromNode].typeNode == 13:
                    pass
                elif currentDirection == previousDirection and type(graphObject.dictNodesPure[connection.fromNode]) is PlayerNode:
                    pass
                else:
                    tmpList.append(node)
                    break
    
    for node in tmpList:
        selectedNodesList.remove(node)
    
    for node in selectedNodesList:
        listIdGoals.append(node.id)
    
    # Movement Skills 
    # (Just adding the movements of the skill with cost 0 to the player node should prioritize the use of these by dijkstra)
    
    # Add Here the id of the skills
    listIdMovementSkills = [28, 8] # 28: Double Time  8: Run run run
    
    # If any movement skill is available to use, it will use it, no restrictions of energy for now
    
    listskills = graphObject.players["bearer"]["skills"]
    for skill in listskills:
        if skill["id"] in listIdMovementSkills and skill["status"] == 1:
            skillObjectives = skill["possible_targets"]
            
            for nextCellCoord in skillObjectives:
                nextCell = graphObject.getCell(nextCellCoord)
                nextNode = graphObject.getNode(nextCell["id"])
                connection = MovementSkill(nodeFrom=playerNode, nodeTo=nextNode, infoSkill=skill, cost=0)
                playerNode.listConnections.append(connection)
    
    # Print this if you are debugging to know what function is executing dijkstra 
    #print("SPECIAL STRATEGY PATH CALLS DIJKSTRA")
    #print("DEBUG INIT", listIdGoals)
    goalNode = dijkstra(graphObject, listIdGoals, playerNode.id)
    
    confirmation_flag = False
    if goalNode.id in listIdGoals and goalNode.id == playerNode.id:
        confirmation_flag = True
        for node in selectedNodesList:
            if goalNode.id == node.id:
                goalNode.notes = node.pathConnections
    
    #print("DEBUG INIT", confirmation_flag)
    
    return {"goalNode": goalNode, "confirmation": confirmation_flag}
