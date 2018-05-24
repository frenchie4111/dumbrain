import random

import numpy as np

from ruleset import RuleSet

class Player():
    """
        Defines a mostly generic player. This player has a set of weights and
        will
    """
    def __init__( self, ruleset, weights=[] ):
        assert( issubclass( ruleset.__class__, RuleSet ) )
        self.ruleset = ruleset

        # If no weights were provided, or an empty list was provided
        if( len( weights ) == 0 ):
            weights = self.getDefaultWeights()
        self.weights = weights

    def getDefaultShape( self ):
        """
        Gets the default shape for this players weights
        """
        return [
            ( self.ruleset.getBoardSize() + 1, 11 ),
            ( 11, self.ruleset.getBoardSize() )
        ]

    def getDefaultWeight( self, shape ):
        """
        Given a shape, creates initial weights
        """
        return np.random.standard_normal( size=shape )

    def getDefaultWeights( self ):
        """
        Creates a default set of weights for this player. Used to initialize
        the player if no weights were given
        """
        return map( lambda shape: self.getDefaultWeight( shape ), self.getDefaultShape() )

    def getInputLayer( self, board ):
        input_layer = np.full( ( 1, self.ruleset.getBoardSize() + 1 ), 0 )
        input_layer[ 0 ][ 0 ] = 1
        input_layer[ 0 ][ 1: ] = board
        return input_layer

    def performLayer( self, values, weights ):
        next_values = np.dot( values, weights )
        return next_values

    def performLayers( self, input_layer ):
        output_values = input_layer
        for layer in self.weights:
            output_values = self.performLayer( output_values, layer )
        return output_values

    def softmax( self, x ):
        """Compute softmax values for each sets of scores in x."""
        return np.exp( x ) / np.sum( np.exp( x ), axis=0 )

    def normalizeOutput( self, output ):
        return self.softmax( output )

    def getMoveFromOutput( self, board, normalized_output ):
        for move_choice in normalized_output.argsort()[ ::-1 ]:
            if self.ruleset.isValidMove( board, move_choice ):
                return move_choice;

    def getMove( self, board ):
        # TODO: Maybe we should pass in game instead of board so that the brain
        #       could have access to the history of the current game
        input_layer = self.getInputLayer( board )
        output_values = self.performLayers( input_layer )
        output_values = output_values[ 0 ] # performLayers returns (1,board_size) array, so we have to flatten it one level before softmaxing
        normalized_output = self.normalizeOutput( output_values )
        return self.getMoveFromOutput( board, normalized_output )

class RandomPlayer( Player ):
    def getMove( self, board ):
        choices = []
        for i, val in enumerate( board ):
            if board[ i ] == 0:
                choices.append( i )
        return random.choice( choices )
