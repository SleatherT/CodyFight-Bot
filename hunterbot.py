from config import CKEY, GAMEMODE
from core.client import Client
from core.nodemap import Graph, getMap
from strategies.hunterStrategy import strategyPath, strategyAttack
import time
import multiprocessing
import signal
from functools import partial

# ckeys format = {"your ckey", "your another ckey", etc...}
ckeys = {CKEY}

def loopGames(player, stopFlag, firstExecution=True):
    if firstExecution:
        print("\n Press CTRL + C To Exit, the bot will stop after the current match has ended\n")
        time.sleep(7)
    CountMatchs = 0
    CountWins = 0
    CountLosses = 0
    continuePlaying_flag = True
    while continuePlaying_flag:
        # User Status: # -1: ?  0: Creating the room  1: inGame  2: Game Ended
        statesToExit = [-1, 2]
        idStatus = player.getIdStatus()
        playerTurn_flag = player.getIsPlayerTurn()
        
        if idStatus == 2:
            jsonResponse = player.getJsonResponse()
            winner = player.getWinner()
            playerName = jsonResponse["players"]["bearer"]["name"]
            enemyName = jsonResponse["players"]["opponent"]["name"]
            statement = jsonResponse["verdict"]["statement"]
            if winner == playerName:
                print(f"Winner! You won: {playerName}, Losser: {enemyName} Statement: {statement} \nTimes Won : {CountWins} \nTimes Lossed : {CountLosses}")
                CountWins = CountWins + 1
            else:
                print(f"Defeat! You Won: {enemyName}, Losser: {playerName} Statement: {statement} \nTimes Won : {CountWins} \nTimes Lossed : {CountLosses}")
                CountLosses = CountLosses + 1
            CountMatchs = CountMatchs + 1
        
        if stopFlag is True and idStatus in statesToExit :
            break
        elif idStatus == 1 and playerTurn_flag:
            if stopFlag is True:
                print("\nINFO: The bot will stop after this game!\n")
            
            jsonResponse = player.getJsonResponse()
            goalNode = strategyPath(jsonResponse)
            player.displayInfo()
            print(goalNode.pathConnections)
            
            # First the execution of the attack
            listTargetsConnections = strategyAttack(jsonResponse)
            reLoop_flag = False
            for targetConnection in listTargetsConnections:
                player.cast_skill(connection=targetConnection)
                player.displayInfo()
                # IMPROVE: breaking after the execution of the skill and looping again in case the attack caused the match to end
                # this works well but i dont like how it looks
                reLoop_flag = True
                break

            if reLoop_flag:
                continue
            
            connection = goalNode.pathConnections[0]
            
            skillConfirmation = connection.usedSkill
            if skillConfirmation is True:
                player.cast_skill(connection=connection)
            else:
                player.move_player(connection=connection)
            
            player.displayInfo()
        
        elif idStatus == 1:
            print("waiting for oponent")
            time.sleep(5)
        elif idStatus == -1:
            player.create_room(0)
        elif idStatus == 2:
            player.create_room(0)
        elif idStatus == 0:
            print("Registering players.. waiting 15 seconds")
            time.sleep(15)
        else:
            print(f"Unknown status! {idStatus}")
            


def sigtermHandler(signum, frame, flag):
    flag = True
    print("Received SIGTERM. Finishing bots, wait until the current matchs have ended...")

def bot(player):
    stopFlag = False

    # Linux Stop with Kill Command, signal SIGTERM
    sigtermHandlerArgs = partial(sigtermHandler, stopFlag)
    signal.signal(signal.SIGTERM, sigtermHandlerArgs)
    
    # Windows/Linux Stop sending signal SIGINT (CRTL + C)
    try:
        loopGames(player, stopFlag)
    except KeyboardInterrupt:
        stopFlag = True
        print(f"Bot = {player.ckey[:7]}... Finishing execution! Wait until the current matchs have ended, Don't Press Ctrl + C again please!")
        time.sleep(4)
        loopGames(player, stopFlag, firstExecution=False)
        print(f"Bot = {player.ckey[:7]}... Finished his last match!")
    

if __name__ == "__main__":
    processList = list()
    Count = 0
    for ckey in ckeys:
        player = Client(ckey, multiProcessing=False)
        processList.append(multiprocessing.Process(target=bot, args=(player, )))
        Count = 1 + Count
    
    for process in processList:
        process.start()
        print(f"{Count} Bot started ! ")
        
    
    for process in processList:
        try:
            process.join()
        except KeyboardInterrupt:
            pass
    
    print("All bots finished")
        
