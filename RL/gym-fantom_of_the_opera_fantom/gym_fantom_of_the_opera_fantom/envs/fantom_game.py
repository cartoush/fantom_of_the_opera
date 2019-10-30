from random import shuffle, randrange
import cProfile
import sys
import random
import os
import logging
from logging.handlers import RotatingFileHandler
import json
import socket
from . import protocol

from . import game_globals
from . import agent_inspector as inspector
from . import agent_fantom as fantom

# """
#     server setup
# """
# link = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# # link.setsockopt(socket.IPPROTO_TCP, socket.SO_REUSEADDR, 1)
# host = ''
# # port = 12000
# port = int(sys.argv[1])
# link.bind((host, port))
# # list that will later contain the sockets
# clients = []


"""
    game data
"""
# determines whether the power of the character is used before
# or after moving
permanents, two, before, after = {'pink'}, {
    'red', 'grey', 'blue'}, {'purple', 'brown'}, {'black', 'white'}
# reunion of sets
colors = before | permanents | after | two
# ways between rooms
passages = [{1, 4}, {0, 2}, {1, 3}, {2, 7}, {0, 5, 8},
            {4, 6}, {5, 7}, {3, 6, 9}, {4, 9}, {7, 8}]
# ways for the pink character
pink_passages = [{1, 4}, {0, 2, 5, 7}, {1, 3, 6}, {2, 7}, {0, 5, 8, 9}, {
    4, 6, 1, 8}, {5, 7, 2, 9}, {3, 6, 9, 1}, {4, 9, 5}, {7, 8, 4, 6}]

"""
    game
"""


class Character:
    """
        Class representing the eight possible characters of the game.
    """

    def __init__(self, color):
        self.color, self.suspect, self.position, self.power = color, True, 0, True

    def __repr__(self):
        if self.suspect:
            susp = "-suspect"
        else:
            susp = "-clean"
        return self.color + "-" + str(self.position) + susp

    def display(self):
        return {
            "color": self.color,
            "suspect": self.suspect,
            "position": self.position,
            "power": self.power
        }


class Player:
    """
        Class representing the players, either the inspector (player 0)
        or the fantom (player 1)
    """

    def __init__(self, n, agent=None):
        self.numero = n
        self.role = "inspector" if n == 0 else "fantom"
        self.agent = agent
        
        # this is the game state returned to the step function
        self.question = {"nb_choices": 8}

    def play(self, game):

        charact = self.select(game.active_tiles,
                              game.update_game_state())

        moved_characters = self.activate_power(charact,
                                               game,
                                               before | two,
                                               game.update_game_state())

        self.move(charact,
                  moved_characters,
                  game.blocked,
                  game.update_game_state())

        self.activate_power(charact,
                            game,
                            after | two,
                            game.update_game_state())

    def select(self, t, game_state):
        """
            Choose the character to activate whithin
            the given choices.
        """
        available_characters = [character.display() for character in t]
        question = {"question type": "select character",
                    "data": available_characters,
                    "game state": game_state}
        selected_character = self.agent.answer(question)

        # test
        # range(len(t)) goes until len(t)-1
        if selected_character not in range(len(t)):
            warning_message = (
                ' !  : selected character not in '
                'available characters. Choosing random character.'
            )
            selected_character = random.randint(0, len(t)-1)

        perso = t[selected_character]

        del t[selected_character]
        return perso

    def activate_power(self, charact, game, activables, game_state):
        """
            Use the special power of the character.
        """
        # check if the power should be used before of after moving
        # this depends on the "activables" variable, which is a set.
        if charact.power and charact.color in activables:
            character_color = charact.display()["color"]
            question = {"question type": f"activate {character_color} power",
                        "data": [0, 1],
                        "game state": game_state}
            power_activation = self.agent.answer(question)

            if power_activation == 1:
                power_answer = "yes"
            else:
                power_answer = "no"

            # work
            if power_activation:
                charact.power = False

                # red character
                if charact.color == "red":
                    draw = game.cards[0]
                    if draw == "fantom":
                        game.position_carlotta += -1 if self.numero == 0 else 1
                    elif self.numero == 0:
                        draw.suspect = False
                    del game.cards[0]

                # black character
                if charact.color == "black":
                    for q in game.characters:
                        if q.position in {x for x in passages[charact.position] if x not in game.blocked or q.position not in game.blocked}:
                            q.position = charact.position

                # white character
                if charact.color == "white":
                    for q in game.characters:
                        if q.position == charact.position and charact != q:
                            disp = {
                                x for x in passages[charact.position] if x not in game.blocked or q.position not in game.blocked}

                            # edit
                            available_positions = list(disp)
                            question = {"question type": "white character power",
                                        "data": available_positions,
                                        "game state": game_state}
                            selected_index = self.agent.answer(question)

                            # test
                            if selected_index not in range(len(disp)):
                                warning_message = (
                                    ' !  : selected position not available '
                                    'Choosing random position.'
                                )
                                selected_position = disp.pop()

                            else:
                                selected_position = available_positions[selected_index]

                            q.position = selected_position

                # purple character
                if charact.color == "purple":

                    available_characters = list(colors)
                    question = {"question type": "purple character power",
                                "data": available_characters,
                                "game state": game_state}
                    selected_index = self.agent.answer(question)

                    # test
                    if selected_index not in range(len(colors)):
                        warning_message = (
                            ' !  : selected character not available '
                            'Choosing random character.'
                        )
                        selected_character = colors.pop()

                    else:
                        selected_character = available_characters[selected_index]

                    # y a pas plus simple ?
                    selected_crctr = [x for x in game.characters if x.color
                                      == selected_character][0]
                    charact.position, selected_crctr.position = selected_crctr.position, charact.position

                # brown character
                if charact.color == "brown":
                    # the brown character can take other characters with him
                    # when moving.
                    return [q for q in game.characters if charact.position == q.position]

                # grey character
                if charact.color == "grey":

                    available_rooms = [room for room in range(10)]
                    question = {"question type": "grey character power",
                                "data": available_rooms,
                                "game state": game_state}
                    selected_index = self.agent.answer(question)

                    # test
                    if selected_index not in range(len(available_rooms)):
                        warning_message = (
                            ' !  : selected room not available '
                            'Choosing random room.'
                        )
                        selected_index = random.randint(
                            0, len(available_rooms)-1)
                        selected_room = available_rooms[selected_index]

                    else:
                        selected_room = available_rooms[selected_index]

                    game.shadow = selected_room

                # blue character
                if charact.color == "blue":

                    # choose room
                    available_rooms = [room for room in range(10)]
                    question = {"question type": "blue character power room",
                                "data": available_rooms,
                                "game state": game_state}
                    selected_index = self.agent.answer(question)

                    # test
                    if selected_index not in range(len(available_rooms)):
                        warning_message = (
                            ' !  : selected room not available '
                            'Choosing random room.'
                        )
                        selected_index = random.randint(
                            0, len(available_rooms)-1)
                        selected_room = available_rooms[selected_index]

                    else:
                        selected_room = available_rooms[selected_index]

                    # choose exit
                    passages_work = passages[selected_room].copy()
                    available_exits = list(passages_work)
                    question = {"question type": "blue character power exit",
                                "data": available_exits,
                                "game state": game_state}
                    selected_index = self.agent.answer(question)

                    # test
                    if selected_index not in range(len(available_exits)):
                        warning_message = (
                            ' !  : selected exit not available '
                            'Choosing random exit.'
                        )
                        selected_exit = passages_work.pop()

                    else:
                        selected_exit = available_exits[selected_index]

                    game.blocked = {selected_room, selected_exit}
        return [charact]

    def move(self, charact, moved_characters, blocked, game_state):
        """
            Select a new position for the character.
        """
        pass_act = pink_passages if charact.color == 'pink' else passages
        if charact.color != 'purple' or charact.power:
            disp = {x for x in pass_act[charact.position]
                    if charact.position not in blocked or x not in blocked}

            available_positions = list(disp)
            question = {"question type": "select position",
                        "data": available_positions,
                        "game state": game_state}
            selected_index = self.agent.answer(question)

            # test
            if selected_index not in range(len(disp)):
                warning_message = (
                    ' !  : selected position not available '
                    'Choosing random position.'
                )
                selected_position = disp.pop()

            else:
                selected_position = available_positions[selected_index]

            for q in moved_characters:
                q.position = selected_position

# *********************************************************************************************** #
# Functions for letting the model play

    def agent_play(self, game):

        """
            Choose the character to activate whithin
            the given choices.
        """
        available_characters = [character.display() for character in game.active_tiles]
        self.question = {"question type": "select character",
                    "data": available_characters,
                    "game state": game.game_state}
        yield False
        selected_character = game.answer

        # test
        # range(len(t)) goes until len(t)-1
        if selected_character not in range(len(game.active_tiles)):
            warning_message = (
                ' !  : selected character not in '
                'available characters. Choosing random character.'
            )
            selected_character = random.randint(0, len(game.active_tiles)-1)

        perso = game.active_tiles[selected_character]

        del game.active_tiles[selected_character]
        charact = perso


        game.update_game_state()
        while True:
            """
                Use the special power of the character.
            """
            # check if the power should be used before of after moving
            # this depends on the "activables" variable, which is a set.
            if charact.power and charact.color in before | two:
                character_color = charact.display()["color"]
                self.question = {"question type": f"activate {character_color} power",
                            "data": [0, 1],
                            "game state": game.game_state}
                yield False
                power_activation = game.answer

                if power_activation == 1:
                    power_answer = "yes"
                else:
                    power_answer = "no"

                # work
                if power_activation:
                    charact.power = False

                    # red character
                    if charact.color == "red":
                        draw = game.cards[0]
                        if draw == "fantom":
                            game.position_carlotta += -1 if self.numero == 0 else 1
                        elif self.numero == 0:
                            draw.suspect = False
                        del game.cards[0]

                    # black character
                    if charact.color == "black":
                        for q in game.characters:
                            if q.position in {x for x in passages[charact.position] if x not in game.blocked or q.position not in game.blocked}:
                                q.position = charact.position

                    # white character
                    if charact.color == "white":
                        for q in game.characters:
                            if q.position == charact.position and charact != q:
                                disp = {
                                    x for x in passages[charact.position] if x not in game.blocked or q.position not in game.blocked}

                                # edit
                                available_positions = list(disp)
                                self.question = {"question type": "white character power",
                                            "data": available_positions,
                                            "game state": game.game_state}
                                yield False
                                selected_index = game.answer

                                # test
                                if selected_index not in range(len(disp)):
                                    warning_message = (
                                        ' !  : selected position not available '
                                        'Choosing random position.'
                                    )
                                    selected_position = disp.pop()

                                else:
                                    selected_position = available_positions[selected_index]

                                q.position = selected_position

                    # purple character
                    if charact.color == "purple":

                        available_characters = list(colors)
                        self.question = {"question type": "purple character power",
                                    "data": available_characters,
                                    "game state": game.game_state}
                        yield False
                        selected_index = game.answer

                        # test
                        if selected_index not in range(len(colors)):
                            warning_message = (
                                ' !  : selected character not available '
                                'Choosing random character.'
                            )
                            selected_character = colors.pop()

                        else:
                            selected_character = available_characters[selected_index]

                        # y a pas plus simple ?
                        selected_crctr = [x for x in game.characters if x.color
                                        == selected_character][0]
                        charact.position, selected_crctr.position = selected_crctr.position, charact.position

                    # brown character
                    if charact.color == "brown":
                        # the brown character can take other characters with him
                        # when moving.
                        moved_characters = [q for q in game.characters if charact.position == q.position]
                        break

                    # grey character
                    if charact.color == "grey":

                        available_rooms = [room for room in range(10)]
                        self.question = {"question type": "grey character power",
                                    "data": available_rooms,
                                    "game state": game.game_state}
                        yield False
                        selected_index = game.answer

                        # test
                        if selected_index not in range(len(available_rooms)):
                            warning_message = (
                                ' !  : selected room not available '
                                'Choosing random room.'
                            )
                            selected_index = random.randint(
                                0, len(available_rooms)-1)
                            selected_room = available_rooms[selected_index]

                        else:
                            selected_room = available_rooms[selected_index]

                        game.shadow = selected_room

                    # blue character
                    if charact.color == "blue":

                        # choose room
                        available_rooms = [room for room in range(10)]
                        self.question = {"question type": "blue character power room",
                                    "data": available_rooms,
                                    "game state": game.game_state}
                        yield False
                        selected_index = game.answer

                        # test
                        if selected_index not in range(len(available_rooms)):
                            warning_message = (
                                ' !  : selected room not available '
                                'Choosing random room.'
                            )
                            selected_index = random.randint(
                                0, len(available_rooms)-1)
                            selected_room = available_rooms[selected_index]

                        else:
                            selected_room = available_rooms[selected_index]

                        # choose exit
                        passages_work = passages[selected_room].copy()
                        available_exits = list(passages_work)
                        self.question = {"question type": "blue character power exit",
                                    "data": available_exits,
                                    "game state": game.game_state}
                        yield False
                        selected_index = game.answer

                        # test
                        if selected_index not in range(len(available_exits)):
                            warning_message = (
                                ' !  : selected exit not available '
                                'Choosing random exit.'
                            )
                            selected_exit = passages_work.pop()

                        else:
                            selected_exit = available_exits[selected_index]

                        game.blocked = {selected_room, selected_exit}
            moved_characters = [charact]
            break

        game.update_game_state()
        while True:
            """
                Select a new position for the character.
            """
            blocked = game.blocked
            pass_act = pink_passages if charact.color == 'pink' else passages
            if charact.color != 'purple' or charact.power:
                disp = {x for x in pass_act[charact.position]
                        if charact.position not in blocked or x not in blocked}

                available_positions = list(disp)
                self.question = {"question type": "select position",
                            "data": available_positions,
                            "game state": game.game_state}
                yield False
                selected_index = game.answer

                # test
                if selected_index not in range(len(disp)):
                    warning_message = (
                        ' !  : selected position not available '
                        'Choosing random position.'
                    )
                    selected_position = disp.pop()

                else:
                    selected_position = available_positions[selected_index]

                for q in moved_characters:
                    q.position = selected_position
            break

        game.update_game_state()
        while True:
            """
                Use the special power of the character.
            """
            # check if the power should be used before of after moving
            # this depends on the "activables" variable, which is a set.
            if charact.power and charact.color in after | two:
                character_color = charact.display()["color"]
                self.question = {"question type": f"activate {character_color} power",
                            "data": [0, 1],
                            "game state": game.game_state}
                yield False
                power_activation = game.answer

                if power_activation == 1:
                    power_answer = "yes"
                else:
                    power_answer = "no"

                # work
                if power_activation:
                    charact.power = False

                    # red character
                    if charact.color == "red":
                        draw = game.cards[0]
                        if draw == "fantom":
                            game.position_carlotta += -1 if self.numero == 0 else 1
                        elif self.numero == 0:
                            draw.suspect = False
                        del game.cards[0]

                    # black character
                    if charact.color == "black":
                        for q in game.characters:
                            if q.position in {x for x in passages[charact.position] if x not in game.blocked or q.position not in game.blocked}:
                                q.position = charact.position

                    # white character
                    if charact.color == "white":
                        for q in game.characters:
                            if q.position == charact.position and charact != q:
                                disp = {
                                    x for x in passages[charact.position] if x not in game.blocked or q.position not in game.blocked}

                                # edit
                                available_positions = list(disp)
                                self.question = {"question type": "white character power",
                                            "data": available_positions,
                                            "game state": game.game_state}
                                yield False
                                selected_index = game.answer

                                # test
                                if selected_index not in range(len(disp)):
                                    warning_message = (
                                        ' !  : selected position not available '
                                        'Choosing random position.'
                                    )
                                    selected_position = disp.pop()

                                else:
                                    selected_position = available_positions[selected_index]

                                q.position = selected_position

                    # purple character
                    if charact.color == "purple":

                        available_characters = list(colors)
                        self.question = {"question type": "purple character power",
                                    "data": available_characters,
                                    "game state": game.game_state}
                        yield False
                        selected_index = game.answer

                        # test
                        if selected_index not in range(len(colors)):
                            warning_message = (
                                ' !  : selected character not available '
                                'Choosing random character.'
                            )
                            selected_character = colors.pop()

                        else:
                            selected_character = available_characters[selected_index]

                        # y a pas plus simple ?
                        selected_crctr = [x for x in game.characters if x.color
                                          == selected_character][0]
                        charact.position, selected_crctr.position = selected_crctr.position, charact.position

                    # brown character
                    if charact.color == "brown":
                        # the brown character can take other characters with him
                        # when moving.
                        moved_characters = [
                            q for q in game.characters if charact.position == q.position]
                        break

                    # grey character
                    if charact.color == "grey":

                        available_rooms = [room for room in range(10)]
                        self.question = {"question type": "grey character power",
                                    "data": available_rooms,
                                    "game state": game.game_state}
                        yield False
                        selected_index = game.answer

                        # test
                        if selected_index not in range(len(available_rooms)):
                            warning_message = (
                                ' !  : selected room not available '
                                'Choosing random room.'
                            )
                            selected_index = random.randint(
                                0, len(available_rooms)-1)
                            selected_room = available_rooms[selected_index]

                        else:
                            selected_room = available_rooms[selected_index]

                        game.shadow = selected_room

                    # blue character
                    if charact.color == "blue":

                        # choose room
                        available_rooms = [room for room in range(10)]
                        self.question = {"question type": "blue character power room",
                                    "data": available_rooms,
                                    "game state": game.game_state}
                        yield False
                        selected_index = game.answer

                        # test
                        if selected_index not in range(len(available_rooms)):
                            warning_message = (
                                ' !  : selected room not available '
                                'Choosing random room.'
                            )
                            selected_index = random.randint(
                                0, len(available_rooms)-1)
                            selected_room = available_rooms[selected_index]

                        else:
                            selected_room = available_rooms[selected_index]

                        # choose exit
                        passages_work = passages[selected_room].copy()
                        available_exits = list(passages_work)
                        self.question = {"question type": "blue character power exit",
                                    "data": available_exits,
                                    "game state": game.game_state}
                        yield False
                        selected_index = game.answer

                        # test
                        if selected_index not in range(len(available_exits)):
                            warning_message = (
                                ' !  : selected exit not available '
                                'Choosing random exit.'
                            )
                            selected_exit = passages_work.pop()

                        else:
                            selected_exit = available_exits[selected_index]

                        game.blocked = {selected_room, selected_exit}
            moved_characters = [charact]
            break
        yield True

class Game:
    """
        Class representing a full game until either the inspector
        of the fantom wins.
    """

    def __init__(self, players):
        self.done = False
        self.players = players
        self.position_carlotta, self.exit, self.num_tour, self.shadow, x = 4, 22, 1, randrange(
            10), randrange(10)
        self.blocked = {x, passages[x].copy().pop()}
        self.blocked_list = list(self.blocked)
        self.characters = {Character(c) for c in colors}
        # tiles are used to draw characters
        self.tiles = [p for p in self.characters]
        # cards are for the red character
        self.cards = self.tiles[:]
        self.fantom = self.cards[randrange(8)]
        self.cards.remove(self.fantom)
        self.cards += ['fantom']*3

        # work
        shuffle(self.tiles)
        shuffle(self.cards)
        for i, p in enumerate(self.tiles):
            p.position = i

        self.characters_display = [character.display() for character in
                                   self.characters]
        self.tiles_display = [tile.display() for tile in
                              self.tiles]

        self.game_state = {
            "position_carlotta": self.position_carlotta,
            "exit": self.exit,
            "num_tour": self.num_tour,
            "shadow": self.shadow,
            "blocked": self.blocked_list,
            "characters": self.characters_display,
            "tiles": self.tiles_display,
        }


        self.player_in_training = players[0] if players[0].agent is None else players[1]
        game_globals.gtrained_player = self.player_in_training.role
        self.gen_step = self.tour()
    def lumiere(self):
        partition = [{p for p in self.characters if p.position == i}
                     for i in range(10)]
        if len(partition[self.fantom.position]) == 1 or self.fantom.position == self.shadow:
            self.position_carlotta += 1
            for piece, gens in enumerate(partition):
                if len(gens) > 1 and piece != self.shadow:
                    for p in gens:
                        p.suspect = False
        else:
            for piece, gens in enumerate(partition):
                if len(gens) == 1 or piece == self.shadow:
                    for p in gens:
                        p.suspect = False
        self.position_carlotta += len(
            [p for p in self.characters if p.suspect])

    def tour(self):
        # work
        player_actif = self.num_tour % 2
        
        if player_actif == 1:
            shuffle(self.tiles)
            self.active_tiles = self.tiles[:4]
        else:
            self.active_tiles = self.tiles[4:]
        
        ##AI playing first
        if self.players[player_actif].agent is None:
            play_agent = self.players[player_actif].agent_play(self)
            for _ in play_agent:
                yield False
            self.players[(player_actif + 1) % 2].play(self)
            self.players[(player_actif + 1) % 2].play(self)
            play_agent = self.players[player_actif].agent_play(self)
            for q in play_agent:
                if q is False:
                    yield False
                else:
                    break
        else:
            self.players[player_actif].play(self)
            play_agent = self.players[player_actif].agent_play(self)
            for _ in play_agent:
                yield False
            play_agent = self.players[player_actif].agent_play(self)
            for q in play_agent:
                if q is False:
                    yield False
                else:
                    break
            self.players[player_actif].play(self)
        
        self.lumiere()
        for p in self.characters:
            p.power = True
        self.num_tour += 1
        yield True

    def step(self, answer):
        # work
        self.answer = answer
        if answer >= self.player_in_training.question["nb_choices"]:
            game_globals.ganswer_correct_range = self.player_in_training.question["nb_choices"] - answer * 5
        game_globals.gnb_suspects = len([p for p in self.characters if p.suspect])
        if self.position_carlotta < self.exit and game_globals.gnb_suspects > 1:
            if next(self.gen_step) is True:
                self.gen_step = self.tour()
            self.player_in_training.question["nb_choices"] = len(self.player_in_training.question["data"])
        if self.position_carlotta >= self.exit:
            self.done = True
            game_globals.gwinner = "fantom"
        elif game_globals.gnb_suspects == 1:
            self.done = True
            game_globals.gwinner = "inspector"
        return self.player_in_training.question, game_globals.calc_reward(True), self.done, {}

    def __repr__(self):
        message = f"Tour: {self.num_tour},\n"
        message += f"Position Carlotta / exit: {self.position_carlotta}/{self.exit},\n"
        message += f"Shadow: {self.shadow},\n"
        message += f"blocked: {self.blocked}"
        message += "".join(["\n"+str(p) for p in self.characters])
        return message

    def update_game_state(self):
        """
            representation of the global state of the game.
        """
        self.characters_display = [character.display() for character in
                                   self.characters]
        self.tiles_display = [tile.display() for tile in
                              self.tiles]
        # update
        self.game_state = {
            "position_carlotta": self.position_carlotta,
            "exit": self.exit,
            "num_tour": self.num_tour,
            "shadow": self.shadow,
            "blocked": self.blocked_list,
            "characters": self.characters_display,
            "tiles": self.tiles_display,
        }

        game_globals.update_game_state(self.game_state)
        return self.game_state

"""
    The order of connexion of the sockets is important.
    inspector is player 0, it must be represented by the first socket.
    fantom is player 1, it must be representer by the second socket.
"""
