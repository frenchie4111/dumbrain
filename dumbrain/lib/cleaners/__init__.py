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

class ColumnCleaner( DataCleaner ):
    def __init__( self, column_name ):
        super( ColumnCleaner, self ).__init__()
        self.column_name = column_name

class DummyColumnCleaner( ColumnCleaner ):
    def __init__( self, column_name, all_values ):
        super( DummyColumnCleaner, self ).__init__( column_name )
        self.all_values = all_values

    def clean( self, data ):
        data = data.copy()
        dummy_cols = pd.get_dummies( data[ self.column_name ], prefix='' )
        dummy_cols = dummy_cols.add_suffix( '_' + self.column_name )
        data = data.join( dummy_cols, rsuffix=self.column_name )
        data = data.drop( self.column_name, axis=1 )
        return data

class RemoveColumnCleaner( ColumnCleaner ):
    def clean( self, data ):
        if self.column_name in data.columns:
            return data.drop( self.column_name, axis=1 )
        return data

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

class BasicTokenSentimentColumnCleaner( ColumnCleaner ):
    def __init__( self, column_name, train_data, score_column_name, omit=[], minlen=2 ):
        super( NameSentimentColumnCleaner, self ).__init__( column_name )
        self.train_data = train_data
        self.score_column_name = score_column_name
        self.omit = omit
        self.minlen = minlen
        self.generateSentiments()

    def tokenize( self, string ):
        strings_to_remove = [ '.', ',', '(', ')', "'", '"' ] + self.omit
        for string_to_remove in strings_to_remove:
            string = string.replace( string_to_remove, '' )
        string = string.lower()
        tokens = string.split( ' ' )
        filtered_tokens = []
        tokens = filter( lambda item: len( item ) >= self.minlen, tokens )
        return list( tokens )

    def generateSentiments( self ):
        tokens = []
        scores = []
        for i, row in self.train_data.iterrows():
            for token in self.tokenize( row[ self.column_name ] ):
                tokens.append( token )
                scores.append( row[ self.score_column_name ] )
        df = pd.DataFrame( { 'tokens': tokens, 'scores': scores } )
        grouped = df.groupby( 'tokens' ).mean()
        grouped = grouped[ df.groupby( 'tokens' ).count()[ 'scores' ] > 5 ]
        self.sentiments = grouped

    def clean( self, data ):
        data = data.copy()
        
        scores = []
        for i, row in data.iterrows():
            tokens = self.tokenize( row[ self.column_name ] )
            score = self.sentiments.iloc[ self.sentiments.index.isin( tokens ) ].mean()[ 'scores' ]
            scores.append( score )
    
        data[ self.column_name + '_score' ] = scores
        return data

def cleanData( _cleaners, _data ):
    for cleaner in _cleaners:
        _data = cleaner.clean( _data )
    return _data
