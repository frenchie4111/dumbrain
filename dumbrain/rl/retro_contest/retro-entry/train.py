# Get our envs before we import tensorflow, incase they need their own tf instance
from multienv import getEnvFns
from anyrl.envs import batched_gym_env
env_fns = getEnvFns()
env = batched_gym_env( env_fns )

import sys
from rainbow import train

output_dir = 'artifacts/model'

if len( sys.argv ) >= 2:
    output_dir = sys.argv[ 1 ]

train( env, output_dir=output_dir )
