import numpy as np
import matplotlib.pyplot as plt

def plotTestSetHistory( test_set_history, result_metric_name ):
    x = np.arange( 1, len( test_set_history ) + 1 )
    y = np.array( list( map( lambda test_set_results: test_set_results.result[ result_metric_name ], test_set_history ) ) )
    plt.plot( x, y )
