import pandas as pd
import numpy as np
import abc

class DataCleaner():
    __metaclass__ = abc.ABCMeta

    def __init__( self ):
        pass

    @abc.abstractmethod
    def clean( self, data ):
        pass

class FilterDataCleaner( DataCleaner ):
    def __init__( self, filter_func ):
        super( FilterClenaer, self ).__init__( column_name )
        self.filter_func = filter_func

    def clean( self, data ):
        return data[ self.filter_func( data ) ]

class FillNaNDataCleaner( DataCleaner ):
    def __init__( self, new_value ):
        super( FillNaNDataCleaner, self ).__init__()
        self.new_value = new_value

    def clean( self, data ):
        return data.fillna( self.new_value )

class ConvertDataCleaner( DataCleaner ):
    def __init__( self, new_type ):
        super( DataCleaner, self ).__init__()
        self.new_type = new_type

    def clean( self, data ):
        return data.astype( self.new_type )

def cleanData( _cleaners, _data ):
    for cleaner in _cleaners:
        _data = cleaner.clean( _data )
    return _data
