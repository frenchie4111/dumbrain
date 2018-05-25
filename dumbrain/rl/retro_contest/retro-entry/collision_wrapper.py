from keras import models
import tensorflow as tf
import numpy as np

from batched_env_wrappers import BatchedObservationWrapper

def fixEmuColors( _obs ):
    """
    Emu Observations are slightly offset from training data due to 9bit color upsampling
    Also normalize the colors by dividing by 255
    """
    _obs = ( _obs / 32 ).astype( np.uint8 ) * 32
    _obs = _obs.astype( np.float32 ) / 255
    return _obs

class CollisionMapWrapper( BatchedObservationWrapper ):
    def __init__( self, env, model_file='models/collision-model-20180525-005107.h5', **args ):
        self.model = models.load_model( model_file )

        self._sess = tf.Session()
        self._images = tf.placeholder( tf.float32, shape=( None, ) + env.observation_space.shape )
        self._grayscale = tf.image.rgb_to_grayscale( self._images )

        super( CollisionMapWrapper, self ).__init__( env, **args )
    
    def observation( self, obses ):
        obses = fixEmuColors( np.array( obses ) )

        col_map = self.model.predict( obses )
        grayscale = self._sess.run( self._grayscale, { self._images: obses } )

        return np.concatenate( ( col_map, grayscale ), axis=-1 )

if __name__ == '__main__':
    import retro
    import matplotlib
    import matplotlib.pyplot as plt

    env = retro.make(
        game='SonicTheHedgehog2-Genesis', 
        state='MetropolisZone.Act1', 
        record='data/record/' 
    )
    wrapper = CollisionMapWrapper( env )

    fig, ( ax1, ax2, ax3 ) = plt.subplots( 1, 3 )

    ax1.xaxis.set_visible(False)
    ax1.yaxis.set_visible(False)
    ax2.xaxis.set_visible(False)
    ax2.yaxis.set_visible(False)
    ax3.xaxis.set_visible(False)
    ax3.yaxis.set_visible(False)

    obs = env.reset()

    env_im = ax1.imshow( obs )

    output = wrapper.observation( [ obs ] )

    print( output.shape )

    ax2.imshow( output[ 0, :, :, 0 ] )
    ax3.imshow( output[ 0, :, :, 1 ] )

    plt.show()