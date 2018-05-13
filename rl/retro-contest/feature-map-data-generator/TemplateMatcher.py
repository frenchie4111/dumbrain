import cv2 as cv
import time

class TemplateMatcher():
    def __init__( self, templates ):
        self.templates = templates
        self._processed_templates = []
        self.init()

    def init( self ):
        for template in self.templates:
            self._processed_templates.append( self.preprocessTemplate( template ) )

    def getTemplates( self ):
        return self._processed_templates

    def preprocessFrame( self, frame ):
        return frame

    def preprocessTemplate( self, template ):
        return template

    def getMask( self, template ):
        return None
    
    def shortCircuit( self, score ):
        return False
    
    def matchTemplate( self, frame ):
        frame = self.preprocessFrame( frame )

        all_results = []

        for template_i, template in enumerate( self.getTemplates() ):
            mask = self.getMask( template, template_i )

            w, h = template.shape[ 0:2 ]

            results = cv.matchTemplate( frame, template, cv.TM_CCORR_NORMED, mask=mask )
            _, score, _, max_loc = cv.minMaxLoc( results )

            results = score, ( max_loc[ 0 ], max_loc[ 1 ] ), ( max_loc[ 0 ] + h, max_loc[ 1 ] + w  ), time.clock() - start_time

            if( self.shortCircuit( results ) ):
                return results
            
            all_results.append( results )
        
        scores = [ sprite_results[ 0 ] for sprite_results in all_sprite_results ]
        highest_score_idx = np.argmax( scores )
        return all_results[ highest_score_idx ]
