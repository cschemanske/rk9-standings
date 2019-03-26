import player as player
from bs4 import BeautifulSoup
import sys

'''

Use class and method definitions in module player.py to process pairings for a provided tournament 
and, given a file with player/deck pairs, process matchup win/loss/tie frequencies based on pairings.

RUNTIME ARGUMENTS: 

-(opt): passing "DEMO" as first argument will demonstrate functionality using Collinsville 2019 Day 2 
pairings and fictional player/deck pairs.

-(opt): passing a filename corresponding to a player/deck list as first argument will use that file 
to assign decks and process archetype win rates.  Currently, dependent on CSV of form (player,deck)

INPUT:

- RK9 pairings hash.  Unique identifer found in each tournament's pairings URL (ex. BD96502A in 
https://player.rk9labs.com/pairings/BD96502A?round=15).

- Round to start analysis: For 1 Day events, generally 1.  For Day 2 Standings, generally 10.

- Round to end analysis: seeking more rounds than exist is protected against, but if wanting to end 
analysis earlier in tournament (say, to produce opp win % tiebreakers without the in-progress round 
factoring), provide desired last round of pairings input.

OUTPUT:

-matchupsJSON.json: provided a filename with player/deck pairs, a json file with deck's win/tie/loss 
frequencies against each other deck in the field. 

-Capable of producing up-to-date standings in with tiebreakers to terminal by printing the 
Tournament object.
'''

def main():

    # Method for demoing functionality.
    try:
        if sys.argv[1] == "DEMO":
            testURL = "https://player.rk9labs.com/pairings/BD96502A?round="
            soup = player.getSoupObjFromURL(testURL+"10")
            startingPairings = player.Pairings(soup,10)
            playerList = player.getPlayerDataFromPairings(startingPairings)
            collinsville = player.Tournament(playerList)

            for i in range(10,16):
                soup2 = player.getSoupObjFromURL(testURL+str(i))
                currPairings = player.Pairings(soup2,i)
                collinsville.progressTournament(currPairings,i)
        
            playersDecks = player.readDecks("testArchetypeCSV.csv")
            player.assignDecks(playersDecks,collinsville)
            collinsville.deckAnalysis("collinsvilleDemoMatchups")
            print(collinsville)
    
        else:
            raise NameError
    except:   
    # get parameters for analysis
        urlStub = "https://player.rk9labs.com/pairings/"
        print("Enter tournament URL hash: ")
        rk9hash = input()
        print("Enter round to start analysis: ")
        startingR = input()
        print("Enter round to end analysis: ")
        endingR = input()
        initialUrl = urlStub + rk9hash + "?round=" + str(startingR)

    # setup tournament object
        soup = player.getSoupObjFromURL(initialUrl)
        startingPairings = player.Pairings(soup,startingR)
        playerList = player.getPlayerDataFromPairings(startingPairings)
        Tournament = player.Tournament(playerList)

    # populate pairings and results
        for i in range(int(startingR),int(endingR)+1):
            soup2 = player.getSoupObjFromURL(urlStub + rk9hash + "?round=" + str(i))
            currPairings = player.Pairings(soup2,i)
            Tournament.progressTournament(currPairings,i)
    
    # handle deck/matchup analysis
        try:
            filename = sys.argv[1]
            playersDecks = player.readDecks(filename) # currently dependent on csv of form (player,deck)
            player.assignDecks(playersDecks,Tournament)
            Tournament.deckAnalysis("matchupsJSON")
        except:
            print("Deck/player file not found.")

        print(Tournament) #uncomment for standings.

if __name__ == "__main__":
    main()