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

def train( batched_env, env_count=1, batch_size_multiplier=32, num_steps=2000000, pretrained_model='artifacts/model/model.cpkt', output_dir='artifacts/model', use_schedules=True ):
    """
    Trains on a batched_env using anyrl-py's dqn and rainbow model.

    env_count: The number of envs in batched_env
    batch_size_multiplier: batch_size of the dqn train call will be env_count * batch_size_multiplier
    num_steps: The number of steps to run training for
    pretrained_model: Load tf weights from this model file
    output_dir: Save tf weights to this file
    use_schedules: Enables the tf_schedules for the train call. Schedules require internet access, so don't include on
        retro-contest evaluation server
    """
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
            print( 'Initializing with random weights' )
            sess.run( tf.global_variables_initializer() )
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

        print( env_count * batch_size_multiplier )

        dqn.train(
            num_steps=num_steps,
            player=player,
            replay_buffer=PrioritizedReplayBuffer(300000, 0.5, 0.4, epsilon=0.1),
            optimize_op=optimize,
            train_interval=env_count,
            target_interval=8192,
            batch_size=env_count * batch_size_multiplier,
            min_buffer_size=max( 4500, env_count * batch_size_multiplier ),
            # min_buffer_size=60,
            tf_schedules=tf_schedules,
            handle_ep=print
        )
        scheduled_saver.save( sess )
