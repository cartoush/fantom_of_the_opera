import gym
from gym import error, spaces, utils
from gym.utils import seeding

import fantom_game
from fantom_game import Player
from fantom_game import Game
import agent_fantom as fantom
import agent_inspector as inspector
import game_globals

class FooEnv(gym.Env):
  metadata = {'render.modes': ['human']}

  def __init__(self):
    self.reset()

  def step(self, action):
    return self.game.step(action)

  def reset(self):
    players = [Player(0, inspector.PlayerInspector(self.nb_session)), Player(
        1, fantom.PlayerFantom(self.nb_session))]
    self.game = Game(players)
    game_globals.reset()


  def render(self, mode='human', close=False):
    ...
