import gym
from model import Model
from a2cagent import A2CAgent
import pandas

import gym_fantom_of_the_opera_fantom

env = gym.make('fantom_of_the_opera_fantom-v0')
# env = gym.make('CartPole-v0')
model = Model(num_actions=env.action_space.n)
obs = env.reset()
print(obs)
print("\n")
df = pandas.DataFrame(obs)
obs = obs[None, :]
print(obs)
action, value = model.action_value(obs)
print("action :")
print(action)
print("value :")
print(value)
agent = A2CAgent(model)
rewards_sum = agent.test(env)
print("%d out of 200" % rewards_sum)
rewards_history = agent.train(env)
print("Finished training, testing...")
print("%d out of 200" % agent.test(env))  # 200 out of 200
