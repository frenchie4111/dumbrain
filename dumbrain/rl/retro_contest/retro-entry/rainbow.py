#!/usr/bin/env python

"""
Train an agent on Sonic using an open source Rainbow DQN
implementation.
"""

# Get our envs before we import tensorflow, incase they need their own tf instance
from multienv import getEnvFns
from anyrl.envs import batched_gym_env
env_fns = getEnvFns()
env = batched_gym_env( env_fns )

print( env.observation_space )

import tensorflow as tf

from anyrl.algos import DQN
from anyrl.models import rainbow_models
from anyrl.rollouts import BatchedPlayer, PrioritizedReplayBuffer, NStepPlayer
from anyrl.spaces import gym_space_vectorizer

from schedules import PeriodicPrinter, ScheduledSaver, LoadingBar, LosswiseSchedule

from batched_env_wrappers import BatchedResizeImageWrapper
from collision_wrapper import CollisionMapWrapper

env = CollisionMapWrapper( env )
env = BatchedResizeImageWrapper( env )

print( env.observation_space )

config = tf.ConfigProto()
config.gpu_options.allow_growth = True # pylint: disable=E1101

with tf.Session( config=config ) as sess:
    dqn = DQN(
        *rainbow_models(
            sess,
            env.action_space.n,
            gym_space_vectorizer( env.observation_space ),
            min_val=-200,
            max_val=200
        )
    )

    scheduled_saver = ScheduledSaver( save_interval=10000, save_dir='artifacts/model/' )

    player = NStepPlayer( BatchedPlayer( env, dqn.online_net ), 3 )
    optimize = dqn.optimize( learning_rate=1e-4 )

    sess.run( tf.global_variables_initializer() )
    print( 'Beginning Training' )

    num_steps = 100000

    dqn.train(
        num_steps=num_steps,
        player=player,
        replay_buffer=PrioritizedReplayBuffer(500000, 0.5, 0.4, epsilon=0.1),
        optimize_op=optimize,
        train_interval=1,
        target_interval=8192,
        batch_size=32,
        min_buffer_size=1000,
        tf_schedules=[
            scheduled_saver,
            PeriodicPrinter(),
            LosswiseSchedule( num_steps )
        ]
    )
    scheduled_saver.save( sess )
