import gym
from gym import error, spaces, utils
from gym.utils import seeding

from . import fantom_game
from .fantom_game import Player
from .fantom_game import Game
from . import agent_fantom as fantom
from . import agent_inspector as inspector
from . import game_globals

class FantomOfTheOperaEnv(gym.Env):
  metadata = {'render.modes': ['human']}

  def __init__(self):
    self.reset()

  def step(self, action):
    return self.game.step(action)

  def reset(self):
    players = [Player(0, inspector.PlayerInspector(game_globals.gnb_session)), Player(
        1, fantom.PlayerFantom(game_globals.gnb_session))]
    self.game = Game(players)
    game_globals.reset()


  def render(self, mode='human', close=False):
    ...
