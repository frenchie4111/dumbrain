import cv2 as cv
import time
import numpy as np

class TemplateMatcher():
    def __init__( self, templates ):
        self.templates = templates
        self._processed_templates = []
        self._frequencies = []
        self.init()

    def init( self ):
        for template in self.templates:
            self._processed_templates.append( self.preprocessTemplate( template ) )
        self._processed_templates = np.array( self._processed_templates )
        self._frequencies = np.zeros( len( self._processed_templates ) )

    def updateFrequencies( self, winner ):
        self._frequencies[ winner ] += 1
            
    def getTemplates( self ):
        return self._processed_templates[ np.argsort( self._frequencies ) ]

    def preprocessFrame( self, frame ):
        return frame

    def preprocessTemplate( self, template ):
        return template, None

    def getMask( self, template, template_i ):
        return None
    
    def shortCircuit( self, results ):
        if results[ 0 ] > 0.95:
            return True
        return False
    
    def matchTemplate( self, frame ):
        frame = self.preprocessFrame( frame )

        all_results = []

        for template_i, template in enumerate( self.getTemplates() ):
            template, mask = template

            w, h = template.shape[ 0:2 ]

            start_time = time.clock()

            results = cv.matchTemplate( frame, template, cv.TM_CCORR_NORMED, mask=mask )
            _, score, _, max_loc = cv.minMaxLoc( results )

            results = score, ( max_loc[ 0 ], max_loc[ 1 ] ), ( max_loc[ 0 ] + h, max_loc[ 1 ] + w  ), time.clock() - start_time

            if( self.shortCircuit( results ) ):
                self.updateFrequencies( template_i )
                return results
            
            all_results.append( results )
        
        scores = [ sprite_results[ 0 ] for sprite_results in all_results ]
        highest_score_idx = np.argmax( scores )
        self.updateFrequencies( highest_score_idx )
        return all_results[ highest_score_idx ]
