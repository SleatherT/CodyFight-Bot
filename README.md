# CodyFight-Bot
Client and Bot for the videogame Codyfight, improvements to make the code more readable, maintainable, etc, are welcome

# Files and Classes
api_request.py contain the function used to make requests to the api, used in the CodyClient.py file

The CodyClient.py the Client Class, this class allows you to send and receive the responses from the server
in a dictionary format, his functions are get_status(), create_room(), cast_skill(), move_player() and surrender(), names are self-explanatory 

pathfinding.py is the larger code and used to get the best path and stablish strategies, you can ignore the majority of small functions
the most important classes and functions are dijkstra(), strategyPath(), createMap()/getMap(), Node Class, Connection Class and Graph Class
you can read the comments to know more about how they work, in resume Graph class creates a map of nodes with his connections from the response received from the api, dijkstra() use the algorithm of his name to calculate the best path to each node and returns the node we want to go, strategyPath() is the main function uses all the info created from the rest of the funtions/classes to stablish strategies to get the path desiered

# How to start
From all the files and functions you only need to import the Client Class from CodyClient.py, strategyPath and createMap from pathfinding.py
Client class only needs your ckey and strategyPath and createMap accepts the response from the server as argument, strategyPath returns a goal node with his information of how to reach to him and createMap a map representation (read the code to know what each character means)

# Operators Supported
For now only operators with swap skill are supported, that doesnt means that you can use other operator with the code, what it means is that the strategyPath() wont take into account the skill of the operator and it wont use it to reach a goal

# Example
The bot.py file has an example of how you should use the main functions
