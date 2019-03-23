import pairings as p
import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
import ssl
import re

class Tournament:
    def __init__(self,playerList):
        self.players = [] # list of all players
        self.playersDict = {} # use an ID to lookup a player.
        self.playersIDDict = {} # use a name to lookup an ID.

        # Create the player objects for each player to track information and dictionary of players.
        ID = 1
        for entry in playerList:
            temp = Player(entry,ID)
            self.players.append(temp)
            self.playersDict[ID] = temp
            ID += 1

        # Create the dict to lookup player ID based on name. 
        ID = 1
        for player in self.players:
            self.playersIDDict[player.name] = ID
            ID += 1
    def progressTournament(self,pairings,currRound):
        for match in pairings.matches:
            # update opponents list, outcomes list, and player match points. 
            self.playersDict[self.playersIDDict[match.player1name]].updateInfoMatch(self.playersDict[self.playersIDDict[match.player2name]],match.player1status,currRound)
            self.playersDict[self.playersIDDict[match.player2name]].updateInfoMatch(self.playersDict[self.playersIDDict[match.player1name]],match.player2status,currRound)
    

    def __str__(self):
        # produces standings
        listOfPlayers = []
        for player in self.players:
            playerOWP = 0
            roundsPlayed = 0
            for outcome in player.matchOutcomes:
                if outcome == "winner" or "tie" or "loser":
                    roundsPlayed += 1
            for opponent in player.opponents:
                playerOWP += opponent.winPercentage
            try:    
                playerOWP = playerOWP/roundsPlayed
            except:
                playerOWP = 0
            playerOWP = round(playerOWP,4)
            temp = (player.name,player.matchPoints,playerOWP)
            listOfPlayers.append(temp)
        
        players = sorted(sorted(listOfPlayers, key = lambda t: float(t[2]),reverse=True),key=lambda t: t[1],reverse=True)

        i = 1
        for player in players:
            print(str(i)+". "+player[0]+": "+str(player[1])+", "+str(player[2]))
            i+=1
        return("")

       
class Player:
    def __init__(self,dataList,num):
        self.deck = ""
        self.ID = num
        self.name = dataList[0]
        self.matchPoints = int(dataList[1])

        self.matchOutcomes = []
        self.opponents = []
        self.roundsPlayed = 0
        self.winPercentage = 0
        
    def calcWinPercentage(self):
        winP = 0
        tieP = 0
        for outcome in self.matchOutcomes:
            if outcome == "winner":
                winP += 1
            if outcome == "tie":
                tieP += 0.5
        try:        
            self.winPercentage = max((winP+tieP)/self.roundsPlayed,0.25)
        except ZeroDivisionError:
            self.winPercentage = 0
        if self.name == "BYE":
            self.winPercentage = 0
        self.winPercentage = round(self.winPercentage,4)

    def setDeck(self,deck):
        self.deck = deck

    def getDeck(self):
        return(self.deck)

    def setMP(self,newMP):
        self.matchPoints = newMP
    
    def getMatchPoints(self):
        return(self.matchPoints)
    
    def updateInfoMatch(self,currOpp,currOutcome,currRound):
        self.matchOutcomes.append(currOutcome)
        self.opponents.append(currOpp)
        self.roundsPlayed += 1

        # accomodate special case for setup of Day 2 Swiss.
        if currRound == 10:
            winMP = 0
            tieMP = 0
        else:
            winMP = 3
            tieMP = 1

        if currOutcome == "winner":
            self.matchPoints += winMP
        if currOutcome == "tie":
            self.matchPoints += tieMP
        if currOutcome == "Random Bye":
            self.matchPoints += winMP

        self.calcWinPercentage()

        
# Get name and current match points from a scrape of pairings.
def getPlayerDataFromPairings(pairings):
    players = []
    # get starting players in a list of format [name,record]
    for match in pairings.matches:
        player = []
        player.append(match.player1name)
        matchPointsFilter = re.compile("\s\d+\s")
        currentMatchPoints = re.findall(matchPointsFilter,match.player1record)
        player.append(currentMatchPoints[0])
        players.append(player)

        if match.player2name == "BYE":
            continue

        else: 
            player = []
            player.append(match.player2name)
            matchPointsFilter = re.compile("\s\d+\s")
            currentMatchPoints = re.findall(matchPointsFilter,match.player2record)
            player.append(currentMatchPoints[0])
            players.append(player)
    
    bye = ["BYE",0]
    players.append(bye)

    # The special case where a player list is being constructed from Round 1 pairings. 
    if pairings.round == 1:
        for player in players:
            player[1] = 0

    return(players)

def main():
    url = "https://player.rk9labs.com/pairings/BD96502A?round=10"
    soup = p.getSoupObjFromURL(url)
    pairings = p.Pairings(soup,10)
    players = getPlayerDataFromPairings(pairings)

if __name__ == "__main__":
    main()