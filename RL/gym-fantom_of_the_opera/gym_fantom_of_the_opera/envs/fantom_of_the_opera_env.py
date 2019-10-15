import gym
from gym import error, spaces, utils
from gym.utils import seeding

import game
from game import Player
from game import Game
import agent_fantom as fantom
import agent_inspector as inspector


class FooEnv(gym.Env):
  metadata = {'render.modes': ['human']}

  def __init__(self):
    self.nb_session = 0
    self.reset()

  def step(self, action):
    self.game.step(action)
    return self.game.game_state, self.game.get_reward(), self.game.done, []

  def reset(self):
    players = [Player(0, inspector.PlayerInspector(self.nb_session)), Player(
        1, fantom.PlayerFantom(self.nb_session))]
    self.game = Game(players)
    self.nb_session += 1


  def render(self, mode='human', close=False):
    ...
