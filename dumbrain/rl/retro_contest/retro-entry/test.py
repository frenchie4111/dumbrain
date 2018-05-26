# Get our envs before we import tensorflow, incase they need their own tf instance
from multienv import getEnvFns
from anyrl.envs import batched_gym_env
env_fns = getEnvFns( bk2dir='data/record/' )
env = batched_gym_env( env_fns )

import sys
from rainbow import train

train( env, output_dir='/tmp/', pretrained_model=None, num_steps=100000 )
