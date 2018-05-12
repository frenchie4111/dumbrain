import retro

env = retro.make(game='SonicTheHedgehog-Genesis', state='GreenHillZone.Act1', record='.')
env.reset()
while True:
    _obs, _rew, done, _info = env.step(env.action_space.sample())
    env.render()
    if done:
        break
