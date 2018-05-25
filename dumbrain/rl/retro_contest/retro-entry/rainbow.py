#!/usr/bin/env python

"""
Train an agent on Sonic using an open source Rainbow DQN
implementation.
"""

import tensorflow as tf

from anyrl.algos import DQN
from anyrl.models import rainbow_models
from anyrl.rollouts import BatchedPlayer, PrioritizedReplayBuffer, NStepPlayer
from anyrl.spaces import gym_space_vectorizer

from schedules import PeriodicPrinter, ScheduledSaver, LoadingBar, LosswiseSchedule

from batched_env_wrappers import BatchedResizeImageWrapper
from collision_wrapper import CollisionMapWrapper

def train( batched_env, num_steps=2000000, pretrained_model='artifacts/model/model.cpkt', output_dir='artifacts/model', use_schedules=True ):
    env = CollisionMapWrapper( batched_env )
    env = BatchedResizeImageWrapper( env )

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

        scheduled_saver = ScheduledSaver( save_interval=10000, save_dir=output_dir )
        print( 'Outputting trained model to', output_dir )

        # Reporting uses BatchedPlayer to get _total_rewards
        batched_player = BatchedPlayer( env, dqn.online_net )
        player = NStepPlayer( batched_player, 3 )

        optimize = dqn.optimize( learning_rate=1e-4 )

        if pretrained_model is None:
            # sess.run( tf.global_variables_initializer() )
            pass
        else:
            print( 'Loading pre-trained model from', pretrained_model )
            scheduled_saver.saver.restore( sess, pretrained_model )

        print( 'Beginning Training, steps', num_steps )

        tf_schedules = []

        if( use_schedules ):
            tf_schedules = [
                scheduled_saver,
                LosswiseSchedule( num_steps, batched_player ),
                LoadingBar( num_steps )
            ]

        dqn.train(
            num_steps=num_steps,
            player=player,
            replay_buffer=PrioritizedReplayBuffer(300000, 0.5, 0.4, epsilon=0.1),
            optimize_op=optimize,
            train_interval=1,
            target_interval=8192,
            batch_size=32,
            min_buffer_size=1000,
            tf_schedules=tf_schedules
        )
        scheduled_saver.save( sess )
