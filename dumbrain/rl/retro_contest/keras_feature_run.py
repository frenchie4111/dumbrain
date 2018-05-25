import retro
import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt
from matplotlib import animation
import numpy as np
import sys

from keras import models, losses
import keras.backend as K

# Some models use the l1_loss function
def l1_loss( y_true, y_pred ):
    print( y_true, y_pred )
    return K.sum( K.abs( y_pred - y_true ), axis=-1)

losses.l1_loss = l1_loss

model = models.load_model( sys.argv[ 1 ] )

movie = retro.Movie( sys.argv[ 2 ] )
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

ax1.xaxis.set_visible(False)
ax1.yaxis.set_visible(False)
ax2.xaxis.set_visible(False)
ax2.yaxis.set_visible(False)

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
