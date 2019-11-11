import numpy as np

def hash_obs(obs):
    if type(obs) == dict:
        hashed_obs = hash_dict(obs)
    elif type(obs) == list:
        hashed_obs = hash_list(obs)
    else: # for CartPole
        hashed_obs = np.array([])
        for a in obs:
            hashed_obs = np.append(hashed_obs, hash(a))
        #hashed_obs = obs
    hashed_obs = hashed_obs[None, :]    
    return hashed_obs

def hash_list(raw):
    hashed_list = np.array([])
    for a in raw:
        if type(a) == list:
            hashed_list = np.append(hashed_list, hash_list(a))
        if type(a) == dict:
            hashed_list = np.append(hashed_list, hash_dict(a))
        else:
            hashed_list = np.append(hashed_list, hash(a))
    return hashed_list

def hash_dict(raw):
    hashed_dict = np.array([])
    for a in raw:
        if type(raw[a]) == list:
            hashed_dict = np.append(hashed_dict, hash_list(raw[a]))
        elif type(raw[a]) == dict:
            hashed_dict = np.append(hashed_dict, hash_dict(raw[a]))
        else:
            hashed_dict = np.append(hashed_dict, hash(raw[a]))
        if a == 'data': # padding data so it's always the same size
            padding = (29 - len(hashed_dict))
            #print("DATAAAAAAAAAAAAAAAAAA --- ", len(hashed_dict))
            if padding > 0:
                hashed_dict = np.append(hashed_dict, [0] * padding)
                #print("after --- ", len(hashed_dict))
            else:
                print("===> ERROOOOOR: data is already too long !!!!")
    return hashed_dict
