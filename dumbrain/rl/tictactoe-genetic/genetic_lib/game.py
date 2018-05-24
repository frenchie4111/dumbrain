import random
import numpy as np

from player import Player
from ruleset import RuleSet

class Game():
    """
        A single instance of a game, takes two players and a ruleset pits 
        them against eachother, to the death
        
        Note: right now it only supports 2 player games
    """
    def __init__( self, ruleset, players, first_player=-1 ):
        assert( len( players ) == 2 ) # For right now only allow 2 players
        for player in players:
            assert( issubclass( player.__class__, Player ) )
        assert( issubclass( ruleset.__class__, RuleSet ) )

        self.players = players
        self.ruleset = ruleset
        self.first_player = first_player

        self.reset()

    def getConvertedBoard( self, current_player_num, is_first_player ):
        """
            Because the brains of the players expect the board to be 1 for them
            and -1 for opponents, when it's not the first players turn we have
            to flip the board
        """
        if is_first_player:
            return self.board
        return self.board * -1

    def getFirstPlayer( self ):
        """
            If we were init with a first_player, use that player, otherwise choose
            a random one
        """
        if( self.first_player == -1 ):
            return random.randint( 0, len( self.players ) - 1 )
        return self.first_player

    def getMove( self, current_player_num, is_first_player ):
        converted_board = self.getConvertedBoard( current_player_num, is_first_player )
        return self.players[ current_player_num ].getMove( converted_board )

    def nextPlayer( self, current_player_num ):
        return ( current_player_num + 1 ) % len( self.players )

    def play( self ):
        self.reset()
        first_player = self.getFirstPlayer()
        current_player_num = first_player

        turn_counter = 0
        winner = 0

        while turn_counter < self.ruleset.getBoardSize() and winner == 0:
            is_first_player = ( current_player_num == first_player )
            move = self.getMove( current_player_num, is_first_player )
            assert( self.ruleset.isValidMove( self.board, move ) )
            self.board[ move ] = 1 if is_first_player else -1
            current_player_num = self.nextPlayer( current_player_num )
            turn_counter += 1
            winner = self.ruleset.getWinner( self.board )

        # We need to convert the winner to back to array indices (or None)
        converted_winner = None
        if winner == 1: # first player won
            converted_winner = first_player
        if winner == -1: # second player won
            converted_winner = self.nextPlayer( first_player )

        return converted_winner, turn_counter, first_player

    def reset( self ):
        self.board = np.full( ( self.ruleset.getBoardSize() ), 0 )
