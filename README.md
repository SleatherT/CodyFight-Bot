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

The **core** folder as his name implies, has the framework to make possible code bots. His files are:
  - client.py contains the Client class use this to make requests to the api, each request sent responds with info that we can use, like the status of the game or if its our turn, the functions of the Client class are get_status(), create_room(), cast_skill(), move_player() and surrender(), names are self-explanatory 
  - nodemap.py has the Graph, Node, Connection classes and the dijkstra, getMap functions, you can see his properties and get an idea of what information they hold

The **strategies** folder has some strategies i have build to some codyfigthers:
  - baseStrategy.py as his name says is a example of a basic strategy using the classes and data obtained from the Graph, you can use it as a point of start for your own strategy
  - swapStrategy.py this is a more complex strategy for the Trickster codyfigther with swap
  - hunterStrategy. build for Hunter codyfigther, in comparison to the swapStrategy the strategyAttack function is more developed here

The **tests** folder has files to test the code:
  - testmap.txt and tests.py, names self-explanatory

Outside we have the bots:
  - swapbot.py is the implementation of all the files mentioned to create a bot to deploy using swapStrategy
  - hunterbot.py same as exitbot using hunterStrategy
  - history.txt everytime we make a request to the api this file is written with the info recieved, if we found a map that cause errors or we want to test something we can copy one of the responses in the testmap.py

# How to start
See the baseStrategy.py and some of the bot files to get an idea of how the code works
You are going to see that the graph has a lot of usefull info, as well as the Nodes, their info is pretty usefull if you now how to use it

# Operators Supported
If you want to use a bot to avoid spending time in completing rarity missions use hunterbot if it has some skills that make damage, otherwise use swapbot.
If you want a solid strategy for now you must create it unless you have a Hunter or a Trickster with Swap, in that case you can use the hunterbot or swapbot

# Deploy bot
To deploy the bot just edit the exitbot.py or hunterbot.py file with your ckey and execute this file
```
player = Client(ckey="your key")

