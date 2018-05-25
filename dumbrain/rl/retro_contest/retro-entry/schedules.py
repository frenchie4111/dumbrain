import os
from tqdm import tqdm
from dumbrain.lib.download import mkdirp
import GPUtil as GPU
import numpy as np

import sys

import tensorflow as tf

import losswise

losswise.set_api_key( 'HMR4DB5IE' )

class TFSchedule():
    time = 0

    def add_time( self, sess, additional_time ):
        self.time += additional_time
        self.tick( sess, self.time )
    
    def tick( self, sess, time ):
        pass

class ScheduledSaver( TFSchedule ):
    def __init__( self, save_interval=1000, save_dir='data/model/' ):
        import tensorflow as tf
        self.saver = tf.train.Saver()
        self.save_interval = save_interval

        self.save_dir = save_dir
        mkdirp( self.save_dir )
        self.save_path = os.path.join( self.save_dir, 'model.cpkt' )

    def save( self, sess, should_print=True ):
        self.saver.save( sess, self.save_path )
        if should_print:
            print( 'Saved', self.save_path )

    def tick( self, sess, time ):
        if time % self.save_interval == 0:
            self.save( sess )

class LoadingBar( TFSchedule ):
    def __init__( self, iters ):
        self.bar = tqdm( total=iters )

    def add_time( self, sess, time ):
        self.bar.update( time )

class PeriodicPrinter( TFSchedule ):
    def __init__( self, dqn, print_interval=1000 ):
        self.print_interval = print_interval
        self.dqn = dqn

    def tick( self, sess, time ):
        if time % self.print_interval == 0:
            print( 'Time', time )

class LosswiseSchedule( TFSchedule ):
    def __init__( self, max_iter ):
        self.session = losswise.Session( tag='losses', max_iter=max_iter )
        self.graph = self.session.graph( 'gpu_stats', kind='min' )
        GPUs = GPU.getGPUs()
        self.gpu = GPUs[ 0 ]

    def tick( self, sess, time ):
        if not np.isnan( time ):
            self.graph.append( 
                time, {
                    'memory_util': self.gpu.memoryUtil * 100,
                    'load': self.gpu.load * 100,
                } 
            )
