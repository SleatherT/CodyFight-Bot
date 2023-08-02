# CodyFight-Bot
Client and Bot for the videogame Codyfight, improvements to make the code more readable, maintainable, etc, are welcome

# Files and Classes
client.py contains the Client class use this to make requests to the api, each request sent responds with info that we can use, like the status of the game or if its our turn, the functions of the Client class are get_status(), create_room(), cast_skill(), move_player() and surrender(), names are self-explanatory 

nodemap.py has the Graph, Node, Connection classes and the dijkstra, getMap functions

baseStrategy.py as his name says is a example of a basic strategy using the classes and data obtained from the Graph

strategy.py this is a more complex strategy for the swap codyfigthers

exitbot.py is the implementation of all the files mentioned to create a bot to deploy

testmap.txt and tests.py are files to test that modifications on the code are not raising errors

history.txt everytime we make a request to the api this file write the info recieved, if we found a map that cause errors or we want
to test something we can copy one of the responses in the testmap.py

# How to start
See the basebot.py and exitbot.py files to get an idea of how the code works
You are going to see that the graph has a lot of usefull info, as well as the Nodes, his info is pretty usefull if you now how to use it

# Operators Supported
For now only operators with swap skill are supported, that doesnt means that you can't use other operator, what it means is that the strategyPath() wont take into account the skill of the operator and it wont use it to reach a goal

# Example
exitbot.py is a great example of how to use the Client and strategyPath function
