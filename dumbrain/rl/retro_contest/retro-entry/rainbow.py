#!/usr/bin/env python

"""
Train an agent on Sonic using an open source Rainbow DQN
implementation.
"""

import tensorflow as tf

from anyrl.algos import DQN
from anyrl.envs import BatchedGymEnv
from anyrl.envs.wrappers import BatchedFrameStack
from anyrl.models import rainbow_models
from anyrl.rollouts import BatchedPlayer, PrioritizedReplayBuffer, NStepPlayer
from anyrl.spaces import gym_space_vectorizer
import gym_remote.exceptions as gre

import retro
from tqdm import tqdm
from env_wrappers import AllowBacktracking, SonicDiscretizer
from schedules import PeriodicPrinter, ScheduledSaver, LoadingBar, LosswiseSchedule

import retrowrapper
from retro_contest.local import make

import os

import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

retrowrapper.set_retro_make( make )

game_state_pairs = []
envs = []
for game in [ 'SonicTheHedgehog-Genesis', 'SonicTheHedgehog2-Genesis', 'SonicAndKnuckles3-Genesis' ]:
    for state in retro.list_states( game ):
        game_state_pairs.append( [ game, state ] )

        env = retrowrapper.RetroWrapper( game, state=state )

        env = AllowBacktracking( env )
        env = SonicDiscretizer( env )

        envs.append( env )

env = BatchedGymEnv( [ envs ] )

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
    eprint( 'Beginning Training' )

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
