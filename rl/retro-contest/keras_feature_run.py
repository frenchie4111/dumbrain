import retro
import matplotlib.pyplot as plt
from matplotlib import animation
import numpy as np

from keras import models, losses
import keras.backend as K

def l1_loss( y_true, y_pred ):
    print( y_true, y_pred )
    return K.sum( K.abs( y_pred - y_true ), axis=-1)

losses.l1_loss = l1_loss

model = models.load_model( 'data/model-20180515-231317.h5' )

movie = retro.Movie( './data/record/SonicTheHedgehog-Genesis-GreenHillZone.Act1-0000.bk2' )
movie.step()

env = retro.make(
    game=movie.get_game(), 
    state=retro.STATE_NONE, 
    use_restricted_actions=retro.ACTIONS_ALL
)
env.initial_state = movie.get_state()
obs = env.reset()

def fixEmuColors( _obs ):
    _obs = ( _obs / 32 ).astype( np.uint8 ) * 32
    _obs = _obs.astype( np.float32 ) / 255
    return _obs

def getPrediction( _obs ):
    return model.predict( fixEmuColors( _obs )[ None, :, :, : ] )[ 0, :, :, 0 ]

fig, ( ax1, ax2 ) = plt.subplots( 1, 2 )

env_im = ax1.imshow( obs )
pred_im = ax2.imshow( getPrediction( obs ) )

SKIP = 350
for i in range( SKIP ):
    movie.step()
    keys = []
    for i in range( env.NUM_BUTTONS ):
        keys.append( movie.get_key( i ) )
    obs, _rew, _done, _info = env.step( keys )

def animate( i ):
    movie.step()
    keys = []
    for i in range( env.NUM_BUTTONS ):
        keys.append( movie.get_key( i ) )
    obs, _rew, _done, _info = env.step( keys )

    env_im.set_data( obs )
    pred_im.set_data( getPrediction( obs ) )

    fig.canvas.draw()

anim = animation.FuncAnimation(
    fig, 
    animate,
    frames=1000,
    interval=50
)

plt.show()
