from anyrl.envs import BatchedGymEnv
from env_wrappers import AllowBacktracking, SonicDiscretizer

import gym_remote.client as grc
import gym_remote.exceptions as gre

env = grc.RemoteEnv( 'tmp/sock' )
env = SonicDiscretizer( env )
env = AllowBacktracking( env )
env = BatchedGymEnv( [ [ env ] ] )

from rainbow import train

try:
    train( env, use_schedules=False )
except gre.GymRemoteError as exc:
    print( 'exception', exc )