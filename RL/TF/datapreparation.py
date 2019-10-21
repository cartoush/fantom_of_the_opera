import gym
import gym_fantom_of_the_opera
import random
import numpy as np
from keras.models     import Sequential
from keras.layers     import Dense
from keras.optimizers import Adam

env = gym.make("fantom_of_the_opera-v0")
env.reset()
score_requirement = 500
initial_games = 1000


def model_data_preparation():
    training_data = []
    accepted_scores = []
    for game_index in range(initial_games):
        score = 0
        game_memory = []
        previous_observation = []
        done = False
        while done is False:
            action = random.randrange(0, 8)
            observation, reward, done, info = env.step(action)

            if len(previous_observation) > 0:
                game_memory.append([previous_observation, action])

            previous_observation = observation
            score += reward
            if done:
                break

        if score >= score_requirement:
            accepted_scores.append(score)
            training_data.append(game_memory)

        print("tour : " + str(game_index) + " score : " + str(score))
        env.reset()

    print(accepted_scores)

    return training_data


def build_model(input_size, output_size):
    model = Sequential()
    model.add(Dense(128, input_dim=input_size, activation='relu'))
    model.add(Dense(52, activation='relu'))
    model.add(Dense(output_size, activation='linear'))
    model.compile(loss='mse', optimizer=Adam())
    return model


def train_model(training_data):
    x = np.array([i[0] for i in training_data]).reshape(-1, len(training_data[0][0]))
    y = np.array([i[1] for i in training_data]).reshape(-1, len(training_data[0][1]))
    g = training_data[0]
    h = training_data[1]
    model = build_model(input_size=len(x[0]), output_size=len(y[0]))

    model.fit(x, y, epochs=10)
    return model


training_data = model_data_preparation()

trained_model = train_model(training_data)

