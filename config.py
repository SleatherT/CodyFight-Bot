# File destined to save configuration values for a modular aproach and Tkinter representation

playerCkey = "your_key" # The key is a string

# --ATTACK CONFIG--

# Change the following variables/flags to True or False depending on what do you want your bot to do and his order of execution
# IMPORTANT: To work as except the order must be a unique number for each ability you are going to use OR repetead orders must have his flag
# set to False leaving only one set to True

# This Flag/Boolean makes the bots prioritize spending energy in killing if a close enemy agent is low life enough to be killed in one hit
prioKill_flag = True
prioKill_name = "prioritizeKill"

# This flag makes the bot target the enemy with less life if there is two or more objectives 
smartTargeting_flag = True
smartTargeting_name = "smartTargeting"

# This flag prioritize one skill, that means this skill is going to be used first and save energy to use it always if possible
prioritizeSkill_flag = True
idPrioritizedSkill = 27

# --ATTACK VARIABLES--

# 2: Push  45: Hit  3: Magnetic Pull 27: Blade Strike  29: Laser Blast  38: Direct Attack  50: Detain

# The listIdDamageSkills is a list with the skills we want the bot to execute
listIdDamageSkills = [38, 45, 27, 3, 29, 50]

# This dictionary defines the order of the attacks, if the bot has several available attacks and targets, this defines in which order should 
# use them, it doesnt overwrite the idPrioritizedSkill variable tho, idPrioritizedSkill is always prioritized over this rule
customOrder = {27: 0,
                29: 2,
                3: 5,
                38: 3,
                45: 4,
                50: 1
                }

# This variables define what nearby agents we want to attack, attacking llama is a no no
listAgentsAttack = [2, 200] # 2: Kix  200: Enemy
listAgentsAvoid = [3, 4, 5, 1] # 3: Llama  4: Ripper 5: Buzz  1: Ryo






# --FINISHING CONFIGURATION--

# Ignore this part unless you are adding a new module, in that case you should now that the configuration of each rule/flag is saved in a dictionary that has his
# name, confirmation of execution and order, the name is used to search and execute the correct code/module in attackModule, this dict is saved in another dict
# that uses the order as key and the dict as value, this is made to sort the modules and execute as planned

# Saving each flag in a dictionary with his name inside a list
tmpList = list()
prioKill_config = {"name": prioKill_name, "confirmation": prioKill_flag, "order":prioKill_order}
tmpList.append(prioKill_config)
smartTargeting_config = {"name": smartTargeting_name, "confirmation": smartTargeting_flag, "order":smartTargeting_order}
tmpList.append(smartTargeting_config)

# Saving all the config values in a dictionary
configAttack = dict()
for skillConfig in tmpList:
    if skillConfig["confirmation"] is False:
        pass
    elif skillConfig["order"] in configAttack:
        for n in range(100):
            if n not in configAttack:
                configAttack[n] = skillConfig
                break
    else:
        configAttack[skillConfig["order"]] = skillConfig