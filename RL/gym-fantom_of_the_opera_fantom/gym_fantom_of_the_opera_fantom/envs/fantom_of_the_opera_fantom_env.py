import gym
from gym import error, spaces, utils
from gym.utils import seeding
import math
import numpy as np

from . import fantom_game
from .fantom_game import Player
from .fantom_game import Game
from . import agent_fantom as fantom
from . import agent_inspector as inspector
from . import game_globals


class FantomOfTheOperaFantomEnv(gym.Env):
  metadata = {'render.modes': ['human']}
  

  def __init__(self):
    self.fail = 0

    # Angle limit set to 2 * theta_threshold_radians so failing observation is still within bounds
    high = np.array([
        self.fail,
        np.finfo(np.float32).max])
    
    self.action_space = spaces.Discrete(8)
    self.observation_space = spaces.Box(-high, high, dtype=np.float32)

    self.reset()

  def step(self, action):
    return self.game.step(action)

  def reset(self):
    players = [Player(0, inspector.PlayerInspector(game_globals.gnb_session)), Player(1)]
    self.game = Game(players)
    game_globals.reset()
    self.game.step(0)
    return self.game.player_in_training.question


  def render(self, mode='human', close=False):
    ...
