import pandas as pd

from dumbrain.lib.cleaners import DataCleaner

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

        for possible_value in self.all_values:
            new_column_name = '_{}_{}'.format( possible_value, self.column_name )
            data[ new_column_name ] = 1
            data[ new_column_name ] = data[ new_column_name ].where( data[ self.column_name ] == possible_value, 0 )

        data = data.drop( self.column_name, axis=1 )

        return data

class RemoveColumnCleaner( ColumnCleaner ):
    def clean( self, data ):
        columns = self.column_name
        if isinstance( columns, str ):
            columns = [ columns ]
            
        for column in columns:
            if column in data.columns:
                data = data.drop( column, axis=1 )

        return data

class MapColumnCleaner( ColumnCleaner ):
    def __init__( self, column_name, map_func, keep=False ):
        super( MapColumnCleaner, self ).__init__( column_name )
        self.map_func = map_func
        self.keep = keep

    def clean( self, data ):
        data = data.copy()
        new_column_name = self.column_name
        if self.keep:
            new_column_name += '_mapped'
        data[ new_column_name ] = data[ self.column_name ].map( self.map_func )
        return data

class CalculatedColumnCleaner( ColumnCleaner ):
    def __init__( self, column_name, map_func ):
        super( CalculatedColumnCleaner, self ).__init__( column_name )
        self.map_func = map_func

    def clean( self, data ):
        data = data.copy()
        data[ self.column_name ] = self.map_func( data )
        return data

class BasicTokenSentimentColumnCleaner( ColumnCleaner ):
    def __init__( self, column_name, train_data, score_column_name, omit=[], minlen=2 ):
        super( BasicTokenSentimentColumnCleaner, self ).__init__( column_name )
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
        # grouped = grouped[ df.groupby( 'tokens' ).count()[ 'scores' ] > 5 ]
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

class QuantileBuckets( ColumnCleaner ):
    def __init__( self, column_name, quantiles, dummy=True ):
        super( QuantileBuckets, self ).__init__( column_name )
        self.q1 = quantiles[ 0 ]
        self.q2 = quantiles[ 1 ]
        self.q3 = quantiles[ 2 ]
        self.dummy = dummy

    def getQuantile( self, value ):
        if value > self.q3:
            return '4'
        if value > self.q2:
            return '3'
        if value > self.q1:
            return '2'
        return '1'

    def clean( self, data ):
        data = MapColumnCleaner( self.column_name, self.getQuantile, keep=True ).clean( data )
        if self.dummy:
            data = DummyColumnCleaner( self.column_name + '_mapped', [ '1', '2', '3', '4' ] ).clean( data )
        return data
