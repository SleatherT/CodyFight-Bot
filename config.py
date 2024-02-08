# Configuration Variables
ImportFailed = False
try:
    from ckey import CKEY
except ImportError:
    ImportFailed = True
    print("ckey.py file not found, use the template to create it!\nUsing ckey of the config.py file\n")
    
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

# Change to False if you want the bot to not use the movement skills (like double time), if its close to his objective, 1 cell
# Usefull if we want to move to a node to cast skills before ending our turn
KEEPMOVESKILL = False

# Change to True to use the special strategy to complete the 4 rarirty mission of the hunter codyfighter
SPECIALSTRAT = True

# This variable defines if the json responses are stored
# Change this variable to False so that it does not save the history, recommended if the bot is deployed in the cloud
# Recommended to keep this change to True if the bot is deployed in a local machina to report bugs if they appear
SAVEHISTORY = True

# Change this variable to True if you want the bot to go only to the exit, basic movement, no strategy, usefull only for missions, not recommended in the long run
# Keep it False and the bot will move towards Ryo if its sorrounded and can be trapped, and against Kix (ONLY APPLIES FOR HUNTERBOT)
GOEXIT = False

# Change this variable to True if you want the bot to prioritize go to Bidirectional tiles, same as GOEXIT, basic movement, no strategy, recommended only for missions
# If this variable is True it will overlap the GOEXIT variable/rule, and the bot will not move towards the exit
GOBIDIRECTIONAL = False