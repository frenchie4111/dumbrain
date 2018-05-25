import retro
from retro_contest.local import make

from anyrl.envs.wrappers import BatchedFrameStack, ResizeImageEnv, GrayscaleEnv
from env_wrappers import AllowBacktracking, SonicDiscretizer

def getEnvFns():
    env_fns = []
    for game in [ 'SonicTheHedgehog-Genesis', 'SonicTheHedgehog2-Genesis', 'SonicAndKnuckles3-Genesis' ]:
        for state in retro.list_states( game ):
            def env_fn():
                env = make( game, state=state )

                env = AllowBacktracking( env )
                env = SonicDiscretizer( env )

                return env

            env_fns.append( env_fn )
    return env_fns
