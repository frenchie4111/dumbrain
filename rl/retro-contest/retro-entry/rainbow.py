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

import retrowrapper
from retro_contest.local import make

retrowrapper.set_retro_make( make )

class TFSchedule():
    time = 0

    def add_time( self, sess, additional_time ):
        self.time += additional_time
        self.tick( sess, self.time )
    
    def tick( self, sess, time ):
        pass

class ScheduledSaver( TFSchedule ):
    def __init__( self, save_interval=1000, save_path='data/model/model.ckpt' ):
        self.saver = tf.train.Saver()
        self.save_interval = save_interval
        self.save_path = save_path

    def tick( self, sess, time ):
        if time % self.save_interval == 0:
            self.saver.save( sess, self.save_path )
            print( 'Saved' )

class LoadingBar( TFSchedule ):
    def __init__( self, iters ):
        self.bar = tqdm( total=iters )

    def add_time( self, sess, time ):
        self.bar.update( time )

game_state_pairs = []
envs = []
for game in [ 'SonicTheHedgehog-Genesis', 'SonicTheHedgehog2-Genesis', 'SonicAndKnuckles3-Genesis' ]:
    for state in retro.list_states( game ):
        game_state_pairs.append( [ game, state ] )

        env = retrowrapper.RetroWrapper( game, state=state )
        # env = TestWrap( game, state=state )
        env = AllowBacktracking( env )
        env = SonicDiscretizer( env )

        envs.append( env )

print( game_state_pairs )

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

    player = NStepPlayer( BatchedPlayer( env, dqn.online_net ), 3 )
    optimize = dqn.optimize( learning_rate=1e-4 )
    sess.run( tf.global_variables_initializer() )
    dqn.train(
        num_steps=30000,
        player=player,
        replay_buffer=PrioritizedReplayBuffer(500000, 0.5, 0.4, epsilon=0.1),
        optimize_op=optimize,
        train_interval=1,
        target_interval=8192,
        batch_size=32,
        min_buffer_size=20000,
        tf_schedules=[
            ScheduledSaver( save_interval=10000 ),
            LoadingBar( 20000 )
        ]
    )

