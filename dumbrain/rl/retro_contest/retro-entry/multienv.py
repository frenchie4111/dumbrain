import retro
from retro_contest.local import make

from anyrl.envs.wrappers import BatchedFrameStack, ResizeImageEnv
from env_wrappers import AllowBacktracking, SonicDiscretizer, Render

def makeEnvFn( game, state ):
    def env_fn():
        env = make( game, state=state )

        env = AllowBacktracking( env )
        env = SonicDiscretizer( env )

        return env
    return env_fn

def getEnvFns():
    env_fns = []
    for game in [ 'SonicTheHedgehog-Genesis', 'SonicTheHedgehog2-Genesis', 'SonicAndKnuckles3-Genesis' ]:
        for state in retro.list_states( game ):
            env_fns.append( makeEnvFn( game, state ) )
    return env_fns
