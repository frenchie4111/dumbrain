import retro

env = retro.make(
    game='SonicTheHedgehog2-Genesis', 
    state='MetropolisZone.Act1', 
    record='data/record/' 
)

obs = env.reset()
for i in range( 1000 ):
    action = env.action_space.sample()
    action[ 7 ] = 1
    env.step( action )
