from anyrl.envs import BatchedGymEnv
from env_wrappers import AllowBacktracking, SonicDiscretizer

import gym_remote.client as grc

env = grc.RemoteEnv( 'tmp/sock' )
env = SonicDiscretizer( env )
env = AllowBacktracking( env )
env = BatchedGymEnv( [ [ env ] ] )

from rainbow import train

train( env, use_schedules=False )
