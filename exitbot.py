from client import Client
from strategy import strategyPath, strategyAttack
from nodemap import getMap
import time

player = Client(ckey="your key")

def loopGames(player):
    CountMatchs = 0
    CountWins = 0
    CountLosses = 0
    continuePlaying_flag = True
    while continuePlaying_flag:
        idStatus = player.getIdStatus()
        playerTurn_flag = player.getIsPlayerTurn()
        if CountMatchs > 1000:
            print(f"1000 Matchs Played! Times Won:{CountWins} Times Lossed:{CountLosses}")
        elif idStatus == 1 and playerTurn_flag:
            jsonResponse = player.getJsonResponse()
            goalNode = strategyPath(jsonResponse)
            listTargetsConnections = strategyAttack(jsonResponse)
            print(getMap(jsonResponse))
            print(goalNode.pathConnections)
            
            # First the execution of the attacks
            for targetConnection in listTargetsConnections:
                coords = targetConnection.positionTo
                idSkill = targetConnection.idSkill
                player.cast_skill(coords["x"], coords["y"], idSkill)
            
            connection = goalNode.pathConnections[0]
            coords = connection.positionTo
            x_coord = coords["x"]
            y_coord = coords["y"]
            
            skillConfirmation = connection.usedSkill
            if skillConfirmation is True:
                idSkill = connection.idSkill
                sJsonResponse = player.cast_skill(x_coord, y_coord, idSkill)
            else:
                player.move_player(x_coord, y_coord)
        elif idStatus == 1:
            print("waiting for oponent")
            time.sleep(5)
        elif idStatus == 2:
            jsonResponse = player.getJsonResponse()
            winner = player.getWinner()
            playerName = jsonResponse["players"]["bearer"]["name"]
            enemyName = jsonResponse["players"]["opponent"]["name"]
            statement = jsonResponse["verdict"]["statement"]
            if winner == playerName:
                print(f"Winner! You won: {playerName}, Losser: {enemyName} Statement: {statement}")
                CountWins = CountWins + 1
                print(f"Times Won : {CountWins}")
                print(f"Times Lossed : {CountLosses}")
            else:
                print(f"Defeat! You Won: {enemyName}, Losser: {playerName} Statement: {statement}")
                CountLosses = CountLosses + 1
                print(f"Times Won : {CountWins}")
                print(f"Times Lossed : {CountLosses}")
            CountMatchs = CountMatchs + 1
            player.create_room(0)
        elif idStatus == 0:
            print("Registering players.. waiting 15 seconds")
            time.sleep(15)
        elif idStatus == -1:
            player.create_room(0)
        else:
            print(f"Unknown status! {idStatus}")
            
loopGames(player)
