from genetic_lib.player import Player
from genetic_lib.ruleset import RuleSet, GenericRuleset
from genetic_lib.game import Game
from genetic_lib.generation import AverageReproduction, WinFitness, Generation

generic_ruleset = GenericRuleset()

player_1 = Player( generic_ruleset )
player_2 = Player( generic_ruleset )

game = Game( generic_ruleset, [ player_1, player_2 ] )

print player_1.weights

print( game.play() )

print player_1.weights
print player_2.weights
print( AverageReproduction().reproduce( [ player_1, player_2 ] ).weights )

fitness = WinFitness()
print( fitness.map( { 'wins': 5 }, { 'won': True } ) )
print( fitness.reduce( { 'wins': 123 } ) )

# gen = Generation( GenericRuleset(), [ player_1, player_2 ], WinFitness(), AverageReproduction() )
# print( gen.run() )
# print( gen.reproduce() )
# 
# print( gen.compareToRandom() )
