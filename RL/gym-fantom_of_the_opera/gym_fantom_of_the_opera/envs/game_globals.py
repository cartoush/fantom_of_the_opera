
#*********************************************************************************#
# Reward management

gold_position_carlotta = 4
gposition_carlotta = 4

gold_nb_suspects = 8
gnb_suspects = 8

gold_game_state = {}
ggame_state = {}

gtrained_player = None
gwinner = None

gnb_session = 0
ganswer_correct_range = 0

greward = 0

def reset():
    global gold_position_carlotta
    global gposition_carlotta
    global gold_nb_suspects
    global gnb_suspects
    global gold_game_state
    global ggame_state
    global gwinner
    global gtrained_player
    global ganswer_correct_range
    global gnb_session

    gold_position_carlotta = 4
    gposition_carlotta = 4

    gold_nb_suspects = 8
    gnb_suspects = 8

    gold_game_state = {}
    ggame_state = {}

    gwinner = None

    ganswer_correct_range = 0
    gnb_session += 1

def update_game_state(game_state):
    global gold_game_state
    global ggame_state

    gold_game_state = ggame_state
    ggame_state = game_state

def calc_reward(ret=False):
    global gold_position_carlotta
    global gposition_carlotta
    global gold_nb_suspects
    global gnb_suspects
    global ggame_state
    global ganswer_correct_range
    global gwinner
    global gtrained_player
    global greward

    nbs = 0
    for char in ggame_state["characters"]:
        if char["suspect"]:
            nbs += 1
    gold_position_carlotta = gposition_carlotta
    gold_nb_suspects = gnb_suspects
    gposition_carlotta = ggame_state["position_carlotta"]
    gnb_suspects = nbs
    if gtrained_player is "fantom":
        carlotta_reward = (gposition_carlotta - gold_position_carlotta)
        suspects_reward = (gnb_suspects - gold_nb_suspects) * 3
    else:
        carlotta_reward = (gold_position_carlotta - gposition_carlotta)
        suspects_reward = (gold_nb_suspects - gnb_suspects) * 3
    
    answer_correct_range = ganswer_correct_range
    ganswer_correct_range = 0
    reward_win = 0
    if gwinner is not None:
        if gwinner is gtrained_player:
            reward_win = 1000
        else:
            reward_win = -1000
    
    reward = float(carlotta_reward + suspects_reward +
                   answer_correct_range + reward_win)
    if ret:
        reward += greward
        greward = 0
    else:
        greward += reward

    return reward

#*********************************************************************************#
