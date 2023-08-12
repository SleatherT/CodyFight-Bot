# CodyFight-Bot
Client and Bot for the videogame Codyfight, improvements to make the code more readable, maintainable, etc, are welcome

# Setting up Python on Windows and Mac
The code is in Python so first we need to install it

Windows

1. Download Python
  - Visit the oficial Python website: python.org
  - Go to the "Downloads" section and choose the latest version for Windows
2. Run the installer
  - Open the downloaded file
  - **Check the box that says "Add Python x.x to PATH" during installation**  __IMPORTANT__
3. Verify the installation
  - Open the Command Prompt or PowerShell
  - Type 'python --version' to verify Python is installed

Mac

1. Check Python Version
  - Mac usually comes with Python pre-installed
  - Open the terminal
  - Type 'python3 --version' to check the version
2. Install Homebrew (if needed):
  - If Python isn't installed or you want to manage versions, install Homebrew: brew.sh
  - Install Python using Homebrew: 'brew install python'
3. Verify Installation
  - Type 'python3 --version' again to confirm Python is installed

# Files and Classes
client.py contains the Client class use this to make requests to the api, each request sent responds with info that we can use, like the status of the game or if its our turn, the functions of the Client class are get_status(), create_room(), cast_skill(), move_player() and surrender(), names are self-explanatory 

nodemap.py has the Graph, Node, Connection classes and the dijkstra, getMap functions

baseStrategy.py as his name says is a example of a basic strategy using the classes and data obtained from the Graph

strategy.py this is a more complex strategy for the swap codyfigthers

exitbot.py is the implementation of all the files mentioned to create a bot to deploy

testmap.txt and tests.py are files to test that modifications on the code are not raising errors

history.txt everytime we make a request to the api this file is written with the info recieved, if we found a map that cause errors or we want to test something we can copy one of the responses in the testmap.py

# How to start
See the basebot.py and exitbot.py files to get an idea of how the code works
You are going to see that the graph has a lot of usefull info, as well as the Nodes, their info is pretty usefull if you now how to use it

# Operators Supported
For now only operators with swap skill are supported, that doesnt means that you can't use other operator, what it means is that the strategyPath() wont take into account the skill of the operator and it wont use it to reach a goal

# Deploy bot
To deploy the bot just edit the exitbot.py file with your ckey and execute this file
```
player = Client(ckey="your key")

