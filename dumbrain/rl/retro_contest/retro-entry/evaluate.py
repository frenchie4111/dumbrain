from anyrl.envs import BatchedGymEnv
from env_wrappers import AllowBacktracking, SonicDiscretizer

import gym_remote.client as grc
import gym_remote.exceptions as gre

env = grc.RemoteEnv( 'tmp/sock' )

env = AllowBacktracking( env )
env = SonicDiscretizer( env )
env = BatchedGymEnv( [ [ env ] ] )

from rainbow import train

try:
    train( env, use_schedules=False, env_count=1, batch_size_multiplier=32, num_steps=1000500, pretrained_model=None )
except gre.GymRemoteError as exc:
    print( 'exception', exc )
