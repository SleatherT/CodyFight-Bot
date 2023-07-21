from CodyClient import Client
from pathfinding import strategyPath, createMap
import time

player = Client(ckey="Your-Key")

def loopGames(player):
    CountMatchs = 0
    CountWins = 0
    CountLosses = 0
    continuePlaying_flag = True
    while continuePlaying_flag:
        idStatus = player.getIdStatus()
        playerTurn_flag = player.getIsPlayerTurn()
        if idStatus == 1 and playerTurn_flag:
            jsonResponse = player.getJsonResponse()
            goalNode = strategyPath(jsonResponse)
            print(createMap(jsonResponse))
            
            connection = goalNode.getFirstConnection()
            coords = connection.getCoordsTo()
            x_coord = coords["x"]
            y_coord = coords["y"]
            
            skillConfirmation = connection.getSkillUsedConfirmation()
            if skillConfirmation is True:
                sJsonResponse = player.cast_skill(x_coord, y_coord)
            else:
                player.move_player(x_coord, y_coord)
        elif idStatus == 1 and playerTurn_flag is False:
            print("waiting for oponent")
            time.sleep(5)
        elif idStatus == 2:
            jsonResponse = player.getJsonResponse()
            winner = player.getWinner()
            playerName = jsonResponse["players"]["bearer"]["name"]
            statement = jsonResponse["verdict"]["statement"]
            if winner == playerName:
                print(f"Winner! Statement: {statement}")
                CountWins = CountWins + 1
                print(f"Times Won : {CountWins}")
                print(f"Times Lossed : {CountLosses}")
            else:
                print(f"Defeat! {statement}")
                CountLosses = CountLosses + 1
                print(f"Times Won : {CountWins}")
                print(f"Times Lossed : {CountLosses}")
            CountMatchs = CountMatchs + 1
            player.create_room()
        elif idStatus == 0:
            print("Registering players.. waiting 5 seconds")
            time.sleep(5)
        elif CountMatchs > 1000:
            print(f"1000 Matchs Played! Times Won:{CountWins} Times Lossed:{CountLosses}")
        else:
            print(f"Unknown status! {idStatus}")
            
loopGames(player)
