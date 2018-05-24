import abc
import random

import numpy as np

from ruleset import RuleSet
from player import Player, RandomPlayer
from game import Game

class Fitness():
    __meta__ = abc.ABCMeta

    @abc.abstractmethod
    def map( self, results ):
        """Takes the results and returns a mapped version of it"""
        pass

    @abc.abstractmethod
    def reduce( self, all_results ):
        """Totals up the results into one number"""
        pass

class WinFitness( Fitness ):
    def map( self, other_results, match_results ):
        if 'wins' not in other_results:
            other_results[ 'wins' ] = 0

        other_results[ 'wins' ] += 1 if match_results[ 'won' ] else 0

        return other_results

    def reduce( self, all_results ):
        return all_results[ 'wins' ]

class Reproduction():
    __meta__ = abc.ABCMeta

    @abc.abstractmethod
    def reproduce( self, players ):
        """Takes two players, reproduces"""
        pass
    
    def selector( self, ordered_population ):
        top_30 = ordered_population[ 0 : 30 ]

        chosen_player_1 = chosen_player_2 = random.choice( top_30 )
        while chosen_player_2 == chosen_player_1:
            chosen_player_2 = random.choice( top_30 )
        
        return [ chosen_player_1, chosen_player_2 ]

class AverageReproduction( Reproduction ):
    def __init__( self, variance=.01 ):
        self.variance = variance

    def averageLayers( self, layers ):
        meaned = np.mean( np.array( layers ), axis = 0 )
        addition = 1 - ( self.variance / 2 ) # we want the variance to be +/- so we do this
        meaned_randomized = meaned * ( ( np.random.random( meaned.shape ) * self.variance ) + addition )
        return meaned_randomized
        
    def reproduce( self, players ):
        child_weights = []
        for i, val in enumerate( players[ 0 ].weights ):
            child_weights.append( self.averageLayers( [ player.weights[ i ] for player in players ] ) )
        return Player( ruleset=players[ 0 ].ruleset, weights=child_weights )

class Generation():
    def __init__( self, ruleset, players, fitness=WinFitness(), reproduction=AverageReproduction(), games=2000 ):
        self.ruleset = ruleset
        self.players = players
        self.fitness = fitness
        self.reproduction = reproduction
        self.games = games

    def compareToRandom( self, games=500 ):
        """
            Plays the current generation against the validation set for a given number of games
            and returns the results
            
            Output
            [
                [wins_going_first, ties_going_first, losses_going_first],
                [wins_not_firsst, ties_not_first, losses_not_first]
            ]
        """
        random_player = RandomPlayer( self.ruleset )
        wins = np.full( ( 2, 3 ), 0 )

        for i in range( games ):
            player = random.choice( self.players )

            game = Game( self.ruleset, [ player, random_player ] )

            results = game.play()

            # If first
            wins_i = 0 if results[ 2 ] == 0 else 1

            wins_i_i = None # win
            if results[ 0 ] == 0:
                wins_i_i = 0
            if results[ 0 ] == None: # tie
                wins_i_i = 1
            if results[ 0 ] == 1: # loss
                wins_i_i = 2

            wins[ wins_i ][ wins_i_i ] += 1
        return wins

    def chooseOpponents( self ):
        """Chooses two random players *indices* the self.players list"""
        player_1_i = player_2_i = random.randint( 0, len( self.players ) - 1 )
        while player_2_i == player_1_i:
            player_2_i = random.randint( 0, len( self.players ) - 1 )
        assert( player_1_i != player_2_i )
        return [ player_1_i, player_2_i ]

    def generateMatchResults( self, game, game_results, matchup_i ):
        return {
            'won': game_results[ 0 ] == matchup_i,
            'went_first': game_results[ 2 ] == matchup_i,
            'game_results': game_results,
            'game': game
        }

    def run( self ):
        results = [ {} for player in self.players ]
        for i in range( self.games ):
            chosen_players_indices = self.chooseOpponents()
            chosen_players = [ self.players[ chosen_players_index ] for chosen_players_index in chosen_players_indices ]

            game = Game( self.ruleset, chosen_players )
            game_results = game.play()

            # We need to call self.fitness.map for each of the players so that we know their results
            for player_choice_array_index, player_index in enumerate( chosen_players_indices ):
                match_results = self.generateMatchResults( game, game_results, player_choice_array_index )
                results[ player_index ] = self.fitness.map( results[ player_index ], match_results )

        results = [ self.fitness.reduce( player_results ) for player_results in results ]
        self.results = results
        return results

    def reproduce( self ):
        results = self.results
        argsorted_results = np.array( results ).argsort()[ ::-1 ]
        sorted_players = [ self.players[ i ] for i in argsorted_results ]

        new_players = []
        for i in range( len( self.players ) ):
            parents = self.reproduction.selector( sorted_players )
            new_players.append( self.reproduction.reproduce( parents ) )

        return Generation( self.ruleset, new_players, self.fitness, self.reproduction, self.games )
