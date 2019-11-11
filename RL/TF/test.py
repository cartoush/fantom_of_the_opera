# disable FutureWarning
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import gym
import hash
from model import Model
from a2cagent import A2CAgent
#import pandas
import numpy as np

import gym_fantom_of_the_opera_fantom

env = gym.make('fantom_of_the_opera_fantom-v0')
model = Model(num_actions=env.action_space.n)
obs = env.reset()
hashed_obs = hash.hash_obs(obs)
action, value = model.action_value(hashed_obs)
agent = A2CAgent(model)
rewards_sum = agent.test(env)
print("\n%d out of 200" % rewards_sum)
rewards_history = agent.train(env)
print("Finished training, testing...")
print("Before training: %d out of 200" % rewards_sum)
print("After training: %d out of 200" % agent.test(env))  # 200 out of 200
