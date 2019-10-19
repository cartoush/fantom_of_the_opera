from gym.envs.registration import register
from .envs.fantom_of_the_opera_env import FantomOfTheOperaEnv

register(
    id='fantom_of_the_opera-v0',
    entry_point='gym_fantom_of_the_opera.envs.fantom_of_the_opera_env:FantomOfTheOperaEnv',
)
