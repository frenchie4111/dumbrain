import cv2 as cv
import time
import numpy as np
import matplotlib.pyplot as plt

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
        argsorted = np.argsort( self._frequencies )
        return self._processed_templates[ argsorted ], argsorted

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
    
    def matchTemplate( self, frame, previous=None ):
        frame = self.preprocessFrame( frame )

        all_results = []

        search_frames = [ ( frame, ( 0, 0 ) ) ]

        frame_width = 5
        if previous is not None:
            previous_tl, previous_br = previous
            previous_frame = frame[ previous_tl[ 1 ] - frame_width : previous_br[ 1 ] + frame_width, previous_tl[ 0 ] - frame_width : previous_br[ 0 ] + frame_width ]
            search_frames.insert( 0, ( previous_frame, ( previous_tl[ 0 ] - frame_width, previous_tl[ 1 ] - frame_width ) ) )

        for search_frame_info in search_frames:
            search_frame, offset = search_frame_info

            templates, template_idx_map = self.getTemplates()
            for template_i, template in enumerate( templates ):
                template, mask = template
                
                if search_frame.shape[ 0 ] < template.shape[ 0 ] or search_frame.shape[ 1 ] < template.shape[ 1 ]:
                    continue

                w, h = template.shape[ 0 : 2 ]

                start_time = time.clock()

                results = cv.matchTemplate( search_frame, template, cv.TM_CCORR_NORMED, mask=mask )
                _, score, _, max_loc = cv.minMaxLoc( results )

                x1 = max_loc[ 0 ] + offset[ 0 ]
                y1 = max_loc[ 1 ] + offset[ 1 ]

                x2 = x1 + h
                y2 = y1 + w

                results = score, ( x1, y1 ), ( x2, y2 ), template_idx_map[ template_i ]

                if( self.shortCircuit( results ) ):
                    self.updateFrequencies( template_i % len( frame ) )
                    return results

                all_results.append( results )

        scores = [ sprite_results[ 0 ] for sprite_results in all_results ]
        highest_score_idx = np.argmax( scores )
        self.updateFrequencies( highest_score_idx % len( frame ) )
        return all_results[ highest_score_idx ]
