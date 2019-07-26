Plant model modelled in this file have 5 variables and is controlled by one control input


PlantModel file can be used as follows

```

from PlantModel import PlantEnvironment

env = PlantEnvironment()

episodeNum = 0
while(i<1000):
  episodeNum = episodeNum + 1
  dinputU = np.random.random()
  state,reward,done = env.step(dinputU)
  env.render()
  
 '''
