import retro
from retro_contest.local import make

from anyrl.envs.wrappers import BatchedFrameStack, ResizeImageEnv
from env_wrappers import AllowBacktracking, SonicDiscretizer, Render

def makeEnvFn( game, state, bk2dir=None ):
    def env_fn():
        env = make( game, state=state, bk2dir=bk2dir )

        env = AllowBacktracking( env )
        env = SonicDiscretizer( env )

        return env
    return env_fn

def getEnvFns( bk2dir=None ):
    env_fns = []
    for game in [ 'SonicTheHedgehog-Genesis', 'SonicTheHedgehog2-Genesis', 'SonicAndKnuckles3-Genesis' ]:
        for state in retro.list_states( game ):
            env_fns.append( makeEnvFn( game, state, bk2dir=bk2dir ) )
    return env_fns
