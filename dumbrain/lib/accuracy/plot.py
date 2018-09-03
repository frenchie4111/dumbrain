import numpy as np
import matplotlib.pyplot as plt

def plotTestSetHistory( test_set_history, result_metric_name ):
    x = np.arange( 1, len( test_set_history ) + 1 )
    y = np.array( list( map( lambda test_set_results: test_set_results.result[ result_metric_name ], test_set_history ) ) )
    plt.plot( x, y )

def plotTestSetHistoryAgainstParameter( test_set_history, result_metric_name, parameter_name ):
    x = np.arange( 1, len( test_set_history ) + 1 )
    y_result = np.array( list( map( lambda test_set_results: test_set_results.result[ result_metric_name ], test_set_history ) ) )
    y_param = np.array( list( map( lambda test_set_results: test_set_results.algorithm.parameters[ parameter_name ], test_set_history ) ) )

    _, ax1 = plt.subplots()
    ax1.set_ylabel( 'result (%s)' % result_metric_name, color='r' )
    ax1.plot( x, y_result, 'r' )

    ax2 = ax1.twinx()
    ax2.set_ylabel( 'parameter (%s)' % parameter_name, color='b' )
    ax2.plot( x, y_param, 'b' )
