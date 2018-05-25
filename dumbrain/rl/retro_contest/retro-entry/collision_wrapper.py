from keras import models
import tensorflow as tf
import numpy as np

from batched_env_wrappers import BatchedObservationWrapper

class CollisionMapWrapper( BatchedObservationWrapper ):
    def __init__( self, env, model_file='models/collision-model-20180525-005107.h5', **args ):
        self.model = models.load_model( model_file )

        self._sess = tf.Session()
        self._images = tf.placeholder( tf.int32, shape=( None, ) + env.observation_space.shape )
        self._grayscale = tf.image.rgb_to_grayscale( self._images )

        super( CollisionMapWrapper, self ).__init__( env, **args )
    
    def observation( self, obses ):
        obses = np.array( obses )
        obses = obses.astype( np.float32 ) / 255.0

        col_map = self.model.predict( obses )

        grayscale = self._sess.run( self._grayscale, { self._images: obses } )

        return np.concatenate( ( col_map, grayscale ), axis=-1 )

if __name__ == '__main__':
    import retro
    retro.make(  )