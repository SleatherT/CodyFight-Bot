# The ckey of the bot must be between quotation marks
# Replace the 'your key' with your key, it should look like this:
# CKEY= "8228bf-..."

CKEY = "your key"

# The numbers corresponding to the game modes can be obtained from the api doc https://codyfight.com/api-doc
# Change this variable if you want to deploy in the other modes
# 0 = Sandbox  /  1 = Friendly Duel  /  3 = Llama Maze
GAMEMODE = 0

# This variable defines if the json responses are stored
# Change this variable to False so that it does not save the history, recommended if the bot is deployed in the cloud
# Recommended to keep this change to True if the bot is deployed in a local machina to report bugs if they appear
SAVEHISTORY = True

# Change this variable to True if you want the bot to go only to the exit, basic movement, no strategy, usefull only for missions, not recommended in the long run
# Keep it False and the bot will move towards Ryo if its sorrounded and can be trapped, and against Kix (ONLY APPLIES FOR HUNTERBOT)
GOEXIT = True