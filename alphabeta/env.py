import logging
import random
from . import GameNode
from . import GameTree
from . import AgentTypes
from . import character

# -- GAME Constants --
MAP_SIZE = 10
MAX_SCORE = 22

## Definition of the various color and when they can trigger their powers
POWER_PERMANENT = {'rose'}
POWER_BEFORE = {"violet", "marron"}
POWER_AFTER = {"noir" , "blanc"}
POWER_BOTH = {"rouge", "gris", "bleu"}
TOTAL_COLORS = POWER_PERMANENT | POWER_BEFORE | POWER_AFTER | POWER_BOTH

## Definition of the paths
ALLOWED_PATH = [{1,4}, {0,2}, {1,3}, {2,7}, {0,5,8}, {4,6}, {5,7}, {3,6,9}, {4,9}, {7,8}]
ROSE_ALLOWED_PATH = [{1,4}, {0,2,5,7}, {1,3,6}, {2,7}, {0,5,8,9}, {4,6,1,8}, {5,7,2,9}, {3,6,9,1}, {4,9,5}, {7,8,4,6}]

class Env:

# passage
#
# 8--------9
# |        |
# |        |
# 4--5--6--7
# |        |
# 0--1--2--3
#

# passage secret
#   ________
#  /        \
# | 8--------9
# | |\      /|
#  \| \    / |
#   4--5--6--7
#   |  |  |  |\
#   0--1--2--3 |
#       \______/
#
    ## MAP
    map = [set() for i in range(MAP_SIZE)]

    score = 0
    
    question_type = ""
    data = []
    
    position_carlotta = 8
    exit = 22
    num_tour = 0

    shadow = 0
    #Locked of the form [roomA, roomB]
    blocked = []

    ## Current non innocent
    characters = []
    innocent = []
    suspect = []

    active_tiles = []

    fantom = None

    gameTree = GameTree.GameTree()

    def __init__(self, *args, **kwargs):
        pass

    def update_infos(self, msg):
        self.question_type = msg["question type"]
        self.question_split = question_type.split()
        self.data = msg["data"]
        game_state = msg["game state"]
        self.position_carlotta = game_state["position_carlotta"]
        self.exit = game_state["exit"]
        self.num_tour = game_state["num_tour"]
        self.show = game_state["shadow"]
        self.blocked = game_state["blocked"]
        self.characters = []
        for char in game_state["characters"]:
            self.characters.append(character.Character(char))
        self.active_tiles = game_state["active tiles"]
        if game_state["fantom"]:
            self.fantom = game_state["fantom"]
        update_characters_status()

    def update_characters_status(self):
        self.innocent = []
        self.suspect = []
        for char in self.characters:
            if char.suspect is True:
                self.suspect.append(char)
            else:
                self.innocent.append(char)
        
    def get_character(self, color):
        for c in self.characters:
            if c.color is color:
                return c

    def get_possible_moves(self, char):
        possible_tiles = ALLOWED_PATH[char.position] if char.color is not "rose" else ROSE_ALLOWED_PATH[char.position]
        try:
            possible_tiles.remove(self.blocked[0])
        except KeyError:
            pass
        try:
            possible_tiles.remove(self.blocked[1])
        except KeyError:
            pass
        return possible_tiles

    def get_characters_at_position(self, pos):
        chars = []
        for char in self.characters:
            if char.position is pos:
                chars.append(char)
        return chars

    def get_role(self):
        return "inspector" if self.fantom == None else "fantom" 
