# Environments For Reinforcement Learning
This Repository contains the Game environments customizable for training models


BlockJump Game can be used as below
"""
from BlockJump import Environment
env = Environment()
env.reset()
for i in range(1000):
  env.render()
  observation, reward, done = env.step()
  if(done == -1):
    print("GameOver")
    print("Final Score obtained is "+str(env.EgoScoreValue))
    break
  elif(done == 1):
    print("You Won")
    print("Final Score obtained is "+str(env.EgoScoreValue))
    break
"""
