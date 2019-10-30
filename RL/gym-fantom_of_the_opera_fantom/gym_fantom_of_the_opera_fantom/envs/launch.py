import fantom_game
import game_globals
import agent_inspector as inspector

players = [fantom_game.Player(0, inspector.PlayerInspector(game_globals.gnb_session)), fantom_game.Player(1)]

game = fantom_game.Game(players)

while True:
    question, reward, done, _ = game.step(0)
    print("question : ")
    print(question)
    print("reward : ")
    print(reward)
    print("done : ")
    print(done)
    if done is True:
        break