
## Import statements
import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
import ssl
import os
'''
class Match:
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
        

def main():
    url = "https://player.rk9labs.com/pairings/BD96502A?round=10"
    soup = getSoupObjFromURL(url)
    round10Pairings = Pairings(soup,10)
    print(round10Pairings)

if __name__ == "__main__":
    main()