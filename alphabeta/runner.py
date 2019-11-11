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
import alphabeta.env as env
import alphabeta.gameagent as gameagent

host = "localhost"
# port = 12000
port = int(sys.argv[1])
# HEADERSIZE = 10

class Player():

    def __init__(self):

        self.end = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self.agent = None
        self.env = env.Env()

    def connect(self):
        self.socket.connect((host, port))

    def reset(self):
        self.socket.close()

    def answer(self, question):
        return self.agent.answer(self.env, question)

    def handle_json(self, data):
        msg = json.loads(data)
        self.env.update_infos(msg)
        if self.agent is None:
            self.agent = gameagent.GameAgent(self.env, self.env.get_role())
        response = self.answer(msg)
        # send back to server
        bytes_data = json.dumps(response).encode("utf-8")
        protocol.send_json(self.socket, bytes_data)

    def run(self):
        self.connect()
        while self.end is not True:
            received_message = protocol.receive_json(self.socket)
            if received_message:
                self.handle_json(received_message)
            else:
                print("no message, finished learning")
                self.end = True


p = Player()

p.run()
