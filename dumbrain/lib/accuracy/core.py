from typing import Dict, List, Type
import time

class Test():
    def __init__( self, input, expected_output, id=None ):
        self.input = input
        self.expected_output = expected_output
        self.id = input if id is None else id

class TestSet():
    def __init__( self, tests, id=None ):
        self.tests = tests
        self.id = id if id is not None else str( time.time() )

class TestOutput():
    def __init__( self, test, output ):
        self.test = test
        self.output = output
    
class TestResult():
    def __init__( self, test_output: TestOutput, result: Dict ):
        self.test_output = test_output
        self.result = result

        self.test = test_output.test

class TestSetResult():
    def __init__( self, test_set: TestSet ):
        self.test_set = test_set
        self.test_results = []
        self.result = None        

    def addTestResult( self, test_result ):
        self.test_results.append( test_result )

    def setResult( self, result: Dict ):
        self.result = result

class Algorithm():
    def _run( self, input ):
        pass

    def run( self, test ) -> TestOutput:
        return TestOutput( test, self._run( test.input ) )

class TestSetResultHandler():
    def __init__( self, test_set ):
        self.test_set_result = TestSetResult( test_set )

    def addOutput( self, test_output: TestOutput ) -> None:
        self.test_set_result.addTestResult( self.handleTestOutput( test_output ) )

    def handleTestOutput( self, test_output: TestOutput ) -> TestResult:
        """
            Map
        """
        return TestResult( test_output, {} )

    def calculateResults( self ) -> TestSetResult:
        """
            Reduce
        """
        return self.test_set_result

class BasicTestResultHandler( TestSetResultHandler ):
    def __init__( self, test_set ):
        super( BasicTestResultHandler, self).__init__( test_set )

        self.valid = 0

    def handleTestOutput( self, test_output ):
        return TestResult( test_output, {
            'valid': 1 if test_output.output == test_output.test.expected_output else 0
        } )

    def calculateResults( self ):
        valids = 0
        for test_result in self.test_set_result.test_results:
            valids += test_result.result[ 'valid' ]

        self.test_set_result.setResult( {
            'percent_correct': valids / len( self.test_set_result.test_results )
        } )

class TestSetGenerator():
    def generate( self ) -> TestSet:
        return []

class OutputHandler():
    def handle( self, test_set_result: TestSetResult ) -> None:
        pass

class LogHandler():
    def handle( self, test_set_result ):
        print( 'Individual tests: ' )
        for test_result in test_set_result.test_results:
            print( '\t', test_result.test.id, test_result.result )
        print( 'Test set:' )
        print( '\t', test_set_result.result )

test_set_generator = None
def testAlgorithm( 
        algorithm: Algorithm, 
        test_set_generator: TestSetGenerator,
        test_set_result_handler_class: Type( TestSetResultHandler ) = BasicTestResultHandler,
        output_handlers: List[ OutputHandler ] = [ LogHandler() ]
    ):
    test_set = test_set_generator.generate()
    test_set_result_handler = BasicTestResultHandler( test_set )

    for test in test_set.tests:
        test_output = algorithm.run( test )
        test_set_result_handler.addOutput( test_output )

    test_set_result_handler.calculateResults()

    for output_handler in output_handlers:
        output_handler.handle( test_set_result_handler.test_set_result )

"""
def MyAlgorithm():
    def _run( self, input ):
        return test.input * 2

test_set_generator = DirectoryGenerator( './Log_Files/' )
testAlgorithm( MyAlgorithm, test_set, output=[ SQLOutput( './my_algo_results.sql' ), LogOutput() ] )
"""

if __name__ == '__main__':
    import random

    class SometimesDoubleAlgorithm( Algorithm ):
        def __init__( self ):
            self.threshold = random.randint( 5, 8 )

        def _run( self, input ):
            if input < self.threshold:
                return input * 2
            return input

    class SequentialTestSetGenerator( TestSetGenerator ):
        def generate( self ):
            tests = []
            for i in range( 9 ):
                tests.append( Test( i, i*2, id=( 'test_' + str( i ) ) ) )
            return TestSet( tests )

    algorithm = SometimesDoubleAlgorithm()
    generator = SequentialTestSetGenerator()
    testAlgorithm( algorithm, generator )
