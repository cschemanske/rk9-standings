import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
import ssl
import re
import csv
import json

# defines tournament object and methods
class Tournament:
    def __init__(self,playerList):
        self.players = [] # list of all players
        self.playersDict = {} # use an ID to lookup a player.
        self.playersIDDict = {} # use a name to lookup an ID.
        self.rounds = 0
        self.archetypes = {}

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
        # adds new pairings, win/loss/tie and opponent results to player object.       
        for match in pairings.matches:
            # update opponents list, outcomes list, and player match points. 
            self.playersDict[self.playersIDDict[match.player1name]].updateInfoMatch(self.playersDict[self.playersIDDict[match.player2name]],match.player1status,currRound)
            self.playersDict[self.playersIDDict[match.player2name]].updateInfoMatch(self.playersDict[self.playersIDDict[match.player1name]],match.player2status,currRound)
            self.rounds += 1
    
    def __str__(self):
        # produces standings w/opp win % tiebreaker
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

    # produces round-by-round results for deck v deck analysis.
    def deckAnalysis(self,filename):
        self.populateArchetypes()
        self.analyzeMatchups()
        self.saveMatchups(filename)
        return()
#The next 3 methods are dependencies for the above method for matchup analysis.
    def populateArchetypes(self):
        temp = {}
        listDecks = []
        for player in self.players:
            if player.name == "BYE":
                continue
            self.archetypes[player.deck] = {}
            listDecks.append(player.deck)
        for entry in self.archetypes:
            for deck in listDecks:
                self.archetypes[entry][deck] = {'winner':0,'loser':0,'tie':0,'Random Bye':0}

    def analyzeMatchups(self):
        for player in self.players:
            i = 0
            if player.name == "BYE":
                continue
            for outcome in player.matchOutcomes:
                if player.opponents[i].name == "BYE":
                    i += 1
                    continue
                self.archetypes[player.deck][player.opponents[i].deck][outcome] = self.archetypes[player.deck][player.opponents[i].deck][outcome] + 1
                i += 1

    def saveMatchups(self,filename):
        with open(filename,'w') as json_file:
            json.dump(self.archetypes,json_file)
       
# Stores player data, including round-by-round opponent (player object), match outcome (win/loss/tie)
# and win percentage (as used in opp win% calculation)
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
        # special cases for random bye
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
    # process round's matches, adding pairings and outcomes to player object.
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

class Match:
    # stores win/loss/tie/still playing status, names, and table number for a match.
    def __init__(self,matchTag):
        self.matchInfo = matchTag('div',class_="text-center")
        try:
            self.tableNumber = str(self.matchInfo[1].contents[2].contents[0].strip())
        except IndexError:
            self.tableNumber = "BYE"
        self.player1name = str(self.matchInfo[0].contents[1].contents[0])+ " " + str(self.matchInfo[0].contents[1].contents[2].strip())
        try:
            self.player1status = str(self.matchInfo[0]["class"][4])
        except IndexError:
            self.player1status = "In Progress"
        self.player1record = str(self.matchInfo[0].contents[2].strip())
        try:
            self.player2name = str(self.matchInfo[2].contents[1].contents[0])+ " " + str(self.matchInfo[2].contents[1].contents[2].strip())
            try: 
                self.player2status = str(self.matchInfo[2]["class"][4])
            except IndexError: 
                self.player2status = "In Progress"
            self.player2record = str(self.matchInfo[2].contents[2].strip())  
        except IndexError:
            self.player2name = "BYE"
            self.player2status = "BYE-loss"
            self.player2record = "BYE-loss"

        if self.player1status == "winner" and self.player2status == "winner":
            self.player1status = "tie"
            self.player2status = "tie" 

        if self.player2name == "BYE":
            self.player1status = "Random Bye"

    def __str__(self):
        return("Table " + self.tableNumber + ": " + self.player1name + " [" + self.player1record + "], " + self.player1status + " vs. " + self.player2name + " [" + self.player2record + "], " + self.player2status)

class Pairings:
    # parsing from RK9 and storing as needed by other objects.
    def __init__(self,soup,round):
        self.tags = soup('div',class_="row match no-gutter")
        self.matches = []
        self.round = round

        for matchTag in self.tags:
            currentMatch=Match(matchTag)
            self.matches.append(currentMatch)
    
    def __str__(self):
        for match in self.matches:
            print(match)
        return("End Round " + str(self.round))
        
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

# Dependency for the CSV-style deck input.
def assignDecks(playersDecks,tournament):
    for entry in playersDecks:
        ID = tournament.playersIDDict[entry[0]]
        player = tournament.playersDict[ID]
        player.deck = entry[1]
        if player.name == "BYE":
            player.deck = "Random Bye"

# read CSV
def readDecks(filename):
    playersLists = []
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file,delimiter=',')
        for line in csv_reader:
            player = line[0].strip()
            deck = line[1].strip()
            playersLists.append([player,deck])
    return(playersLists)

# scrape RK9 for BeautifulSoup obj
def getSoupObjFromURL(url):
    """ return a soup object from the url """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    html = urlopen(url, context=ctx).read()
    soup = BeautifulSoup(html, "html.parser")
    return soup

# testing
def main():
    url = "https://player.rk9labs.com/pairings/BD96502A?round=10"
    url2 = "https://player.rk9labs.com/pairings/BD96502A?round=11"
    soup = getSoupObjFromURL(url)
    pairings = Pairings(soup,10)
    players = getPlayerDataFromPairings(pairings)
    event = Tournament(players)

    soup2 = getSoupObjFromURL(url2)
    pairings2 = Pairings(soup2,11)
    event.progressTournament(pairings,10)
    event.progressTournament(pairings2,11)

    playersDecks = readDecks("testArchetypeCSV.csv")
    assignDecks(playersDecks,event)
    event.populateArchetypes()
    event.analyzeMatchups()
    event.saveMatchups("deckMatchups")

if __name__ == "__main__":
    main()