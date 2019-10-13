import socket
import os
import logging
from logging.handlers import RotatingFileHandler
import json
import protocol
from random import randrange
import random
import time
import sys

host = "localhost"
# port = 12000
port = int(sys.argv[1])
# HEADERSIZE = 10

"""
set up inspector logging
"""
inspector_logger = logging.getLogger()
inspector_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s :: %(levelname)s :: %(message)s", "%H:%M:%S")
filename = "./logs/inspector" + str(port) + ".log"
# file
if os.path.exists(filename):
    os.remove(filename)
file_handler = RotatingFileHandler(filename , 'a', 1000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
inspector_logger.addHandler(file_handler)
# stream
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)
inspector_logger.addHandler(stream_handler)

#*********************************************************************************#
# Reward management
gold_position_carlotta = 4
gposition_carlotta = 4

gold_nb_suspects = 8
gnb_suspects = 8

gold_game_state = {}
ggame_state = {}

gwin = 0

def set_win(res):
    global gwin
    if res == "gwin":
        gwin = 50
    elif res == "lose":
        gwin = -50

def set_values_for_reward(game_state):
    global gold_position_carlotta
    global gposition_carlotta
    global gold_nb_suspects
    global gnb_suspects
    global gold_game_state
    global ggame_state

    nbs = 0
    for char in game_state["characters"]:
        if char["suspect"]:
            nbs += 1
    gold_position_carlotta = gposition_carlotta
    gold_nb_suspects = gnb_suspects
    gposition_carlotta = game_state["position_carlotta"]
    gnb_suspects = nbs
    gold_game_state = ggame_state
    ggame_state = game_state

def evaluate_reward():
    global gold_position_carlotta
    global gposition_carlotta
    global gold_nb_suspects
    global gnb_suspects
    global gwin

    carlotta_reward = (gold_position_carlotta - gposition_carlotta) 
    suspects_reward = (gold_nb_suspects - gnb_suspects) * 3

    return (carlotta_reward + suspects_reward + gwin) * 10

#*********************************************************************************#

class Player():

    def __init__(self):

        self.end = False
        # self.old_question = ""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def connect(self):
        self.socket.connect((host, port))

    def reset(self):
        self.socket.close()

    def answer(self, question):
        # work
        data = question["data"]
        game_state = question["game state"]
        response_index = random.randint(0, len(data)-1)
        # log
        inspector_logger.debug("|\n|")
        inspector_logger.debug("inspector answers")
        inspector_logger.debug(f"question type ----- {question['question type']}")
        inspector_logger.debug(f"data -------------- {data}")
        inspector_logger.debug(f"response index ---- {response_index}")
        inspector_logger.debug(f"response ---------- {data[response_index]}")
        return response_index

    def handle_json(self, data):
        data = json.loads(data)
        print("DATA : \n")
        print(data)
        print("\n")
        print("\n")
        if data["data"] == "win":
            set_win(data["data"])
            self.end = True
            return
        elif data["data"] == "lose":
            set_win(data["data"])
            self.end = True
            return
        #TODO evaluate reward here
        response = self.answer(data)
        # send back to server
        bytes_data = json.dumps(response).encode("utf-8")
        protocol.send_json(self.socket, bytes_data)

    def run(self):

        try:
            self.connect()
        except ConnectionRefusedError as e:
            os.remove(filename)

        while self.end is not True:
            received_message = protocol.receive_json(self.socket)
            if received_message:
                self.handle_json(received_message)
            else:
                print("no message, finished learning")
                self.end = True
        #TODO evaluate reward here

p = Player()

p.run()
