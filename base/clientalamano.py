import socket
import os
import logging
from logging.handlers import RotatingFileHandler
import json
import protocol
from random import randrange
import random
import time
from sys import stdin

host = "localhost"
port = 12000
# HEADERSIZE = 10

"""
set up alamano logging
"""
alamano_logger = logging.getLogger()
alamano_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s :: %(levelname)s :: %(message)s", "%H:%M:%S")
# file
if os.path.exists("./logs/alamano.log"):
    os.remove("./logs/alamano.log")
file_handler = RotatingFileHandler('./logs/alamano.log', 'a', 1000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
alamano_logger.addHandler(file_handler)
# stream
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)
alamano_logger.addHandler(stream_handler)


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
        print("data len : " + str(len(data)) + "\n")
        response_index = int(stdin.read(2))
        # log
        alamano_logger.debug("|\n|")
        alamano_logger.debug("alamano answers")
        alamano_logger.debug(f"question type ----- {question['question type']}")
        alamano_logger.debug(f"data -------------- {data}")
        alamano_logger.debug(f"response index ---- {response_index}")
        alamano_logger.debug(f"response ---------- {data[response_index]}")
        return response_index

    def handle_json(self, data):
        data = json.loads(data)
        print("DATA\n")
        print(data)
        print("\n")
        response = self.answer(data)
        # send back to server
        bytes_data = json.dumps(response).encode("utf-8")
        protocol.send_json(self.socket, bytes_data)

    def run(self):

        self.connect()

        while self.end is not True:
            time.sleep(1)
            received_message = protocol.receive_json(self.socket)
            if received_message:
                self.handle_json(received_message)
            else:
                print("no message, finished learning")
                self.end = True


p = Player()

p.run()
