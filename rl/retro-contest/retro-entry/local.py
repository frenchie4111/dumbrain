from keras import layers, backend as K, losses, models, optimizers
import numpy as np

from PIL import Image

from rl.agents.dqn import DQNAgent
from rl.policy import LinearAnnealedPolicy, BoltzmannQPolicy, EpsGreedyQPolicy
from rl.memory import SequentialMemory
from rl.core import Processor
from rl.callbacks import FileLogger, ModelIntervalCheckpoint

import gym

from env_wrappers import AllowBacktracking

from make_wrapper import make
# from retro_contest.local import make

env = make(
    game='SonicTheHedgehog-Genesis', 
    state='GreenHillZone.Act1', 
    bk2dir='data/record/'
)

env = AllowBacktracking( env )

actual_actions = [
#     B  A  M  S  U  D  L  R  C  Y  X  Z
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ], # {}
    [ 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0 ], # { LEFT }
    [ 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0 ], # { RIGHT }, 
    [ 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0 ], # { LEFT, DOWN }, 
    [ 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0 ], # { RIGHT, DOWN }, 
    [ 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0 ], # { DOWN }, 
    [ 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0 ], # { DOWN, B }, 
    [ 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ]  # { B }
]

INPUT_SHAPE = ( 80, 80 )

class RetroProcessor( Processor ):
    def process_observation( self, obs ):
        img = Image.fromarray( obs )
        img = img.resize( INPUT_SHAPE ).convert( 'L' )

        return np.array( img, dtype=np.uint8 )

    def process_state_batch( self, batch ):
        return batch.astype( np.float32 ) / 255.

    def process_action( self, action ):
        return actual_actions[ action ]

x = input_layer = layers.Input( ( 1,) + INPUT_SHAPE )
x = layers.Permute( ( 2, 3, 1 ) )( x )

# weights = K.constant( [ [ [ [0.21 , 0.72 , 0.07] ] ] ] )
# grayscale = K.sum( x * weights, axis=-1, keepdims=True )
# x = grayscale

x = layers.Conv2D(
    filters=32,
    kernel_size=( 8, 8 ),
    strides=4,
    activation='relu'
)( x )

x = layers.Conv2D(
    filters=64,
    kernel_size=( 4, 4 ),
    strides=2,
    activation='relu'
)( x )

x = layers.Conv2D(
    filters=64,
    kernel_size=( 3, 3 ),
    strides=1,
    activation='relu'
)( x )

x = layers.Flatten()( x )

x = layers.Dense( 512, activation='relu' )( x )
x = layers.Dense( len( actual_actions ), activation='linear' )( x )

model = models.Model( inputs=input_layer, outputs=x )

policy = LinearAnnealedPolicy(
    EpsGreedyQPolicy(), 
    attr='eps', 
    value_max=1., 
    value_min=.1, 
    value_test=.05,
    nb_steps=1000000
)

memory = SequentialMemory( limit=100000, window_length=1 )
processor = RetroProcessor()

dqn = DQNAgent(
    model=model, 
    nb_actions=len( actual_actions ), 
    policy=policy, 
    memory=memory,
    processor=processor, 
    enable_dueling_network=True,
    # action_repetition=4,
    nb_steps_warmup=200, 
    gamma=.99, 
    target_model_update=10000,
    train_interval=1,
    delta_clip=1.
)

dqn.compile( optimizers.Adam( lr=.00025 ), metrics=[ 'mae' ] )

dqn.fit(
    env,
    nb_steps=20000, 
    log_interval=1000
)

# dqn.save_weights( 'data/weights', overwrite=True )

dqn.test( env, nb_episodes=10, visualize=True )
