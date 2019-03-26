# rk9-standings/deck analysis
Generate Standings and Deck from RK9 Live Pairings.

Use class and method definitions in module player.py to process pairings for a provided tournament 
and, given a file with player/deck pairs, process matchup win/loss/tie frequencies based on pairings.

(It can be a tad slow with big tournaments, like Collinsville 2019.)

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

OUTPUT files:

-matchupsJSON: provided a filename with player/deck pairs, a json file with deck's win/tie/loss 
frequencies against each other deck in the field. 

-Capable of producing up-to-date standings with tiebreakers by printing the Tournament object.
'''
