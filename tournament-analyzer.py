import player as player
import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
import ssl
import os
import re

'''
So, it works right now, but to implement starting at Round 1, need to:
- Change the way match points are processed for the first analysis Round OR change how the players are created.
- Change the way URL generation works in this main()
'''

def getSoupObjFromURL(url):
    """ return a soup object from the url """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    html = urlopen(url, context=ctx).read()
    soup = BeautifulSoup(html, "html.parser")
    return soup

def main():
    # input parameters
    urlStub = "https://player.rk9labs.com/pairings/"
    print("Enter tournament URL hash: ")
    rk9hash = input()
    print("Enter round to start analysis: ")
    startingR = input()
    print("Enter round to end analysis: ")
    endingR = input()
    penultimateRound = int(startingR)-1
    initialUrl = urlStub + rk9hash + "?round=" + str(penultimateRound)

    # setup tournament
    soup = getSoupObjFromURL(initialUrl)
    startingPairings = player.p.Pairings(soup,startingR)
    playerList = player.getPlayerDataFromPairings(startingPairings)
    Tournament = player.Tournament(playerList)

    for i in range(int(startingR),int(endingR)+1):
        soup2 = getSoupObjFromURL(urlStub + rk9hash + "?round=" + str(i))
        currPairings = player.p.Pairings(soup2,i)
        Tournament.progressTournament(currPairings)
    
    print(Tournament)

if __name__ == "__main__":
    main()