from gym.envs.registration import register
from .envs.fantom_of_the_opera_fantom_env import FantomOfTheOperaFantomEnv

register(
    id='fantom_of_the_opera_fantom-v0',
    entry_point='gym_fantom_of_the_opera_fantom.envs.fantom_of_the_opera_fantom_env:FantomOfTheOperaFantomEnv',
)
