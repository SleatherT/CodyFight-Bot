import time
# Configuration Variables
ImportFailed = False
try:
    from ckey import CKEY
except ImportError:
    ImportFailed = True
    print("ckey.py file not found, use the ckey.py.template to create it!\nUsing ckey of the config.py file\n")
    time.sleep(3)
    
# Its recommended to use the ckey.py.template file to store your ckey so you don't have to edit this file everytime you are updating the code from github
# If it is complicated for you, you can add your ckey here

# The ckey of the bot must be between quotation marks
# Replace the 'your key' with your key, it should look like this:
# CKEY= "8228bf-..."
if ImportFailed:
    CKEY = 'your key'

# The numbers corresponding to the game modes can be obtained from the api doc https://codyfight.com/api-doc
# Change this variable if you want to deploy in the other modes
# 0 = Sandbox  /  1 = Friendly Duel  /  3 = Llama Maze
GAMEMODE = 0

# This variable defines if the json responses are stored
# Change this variable to False so that it does not save the history, recommended if the bot is deployed in the cloud
# Recommended to keep this change to True if the bot is deployed in a local machina to report bugs if they appear
SAVEHISTORY = True

# Change to False if you want the bot to not use the movement skills (like double time), if its close to his objective, 1 cell
# Usefull if we want to move to a node to cast skills before ending the turn
KEEPMOVESKILL = True

# At XERGO's request. Native skill block
# Set to True if you dont want the bot use the native skill
BLOCK_NATIVE = False

# Change to True to use the special strategy to complete the 4 rarirty mission of the legendary hunter codyfighter
SPECIALSTRAT = False


# 'FOLLOW' CONFIGURATION
# By default a general 'follow' strategy is applied, that is, follow the closest: Exit, Enemy or Kix, follow also Ryo too but only if this is close to be caught (can move only to one tile)

DEFAULT_TARGETS = True

# RULES OF 'FOLLOW'
# If one of the next options are set to True it will overlap the DEFAULT_TARGETS option
# Change to True the targets you want to follow, you can combine depending of the type the bot you are deploying

# If the target is not in the map or it will fallback to the DEFAULT_TARGETS strategy. If you want to dissable this set FALLBACK_TO_DEFAULT to False
FALLBACK_TO_DEFAULT = True

# Names of the options are self-explanatory

GO_ENEMY = False

GO_RYO = False

# Similar to GO_RYO but it will only follow him if its close to be caught
GO_RYO_SURROUNDED = False

GO_KIX = False

GO_LLAMA = False

GO_BUZZ = False

GO_EXIT = False

GO_TELEPORT = False

# XD
GO_RIPPER = False


# ATTACK CONFIGURATION
# Set to True the targets you want to attack, combine with 'FOLLOW' CONFIGURATION to follow and attack specific targets
# Only the attacks that do damage will be executed following this options

# The DEFAULT_ATTACK option is: attack Enemy or Kix
DEFAULT_ATTACK = True

# RULES OF ATTACK
# Similar to follow rules. If one of the below options are True it will overlap DEFAULT_ATTACK option
# Set the targets you want to attack to True

ATTACK_ENEMY = False

ATTACK_RYO = False

ATTACK_KIX = False

ATTACK_LLAMA = False

ATTACK_RIPPER = False

ATTACK_BUZZ = False


# SKILLS CONFIGURATION
# Skills that dont do damage are more tricky to cast, because they need to be executed with an strategy, you cant spend energy in destrying a trap that its 7 km away
# Until this problem solved you can set this variable to True if you want to cast these abilities rondomly, recommended only if you need to complete rarity missions

RANDOM_CAST_SKILLS = False

# NEXT CONFIG OPTION IN WORK:

AVOID_RANGE = 1