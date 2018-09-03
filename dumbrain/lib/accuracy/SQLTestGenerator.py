import sqlite3
import json

from .core import Test, TestSet, TestSetGenerator

class SQLTestGenerator( TestSetGenerator ):
    def __init__( self, sqlite_filename, test_set_id='default' ):
        self.sqlite_filename = sqlite_filename
        self.test_set_id = test_set_id

    fetch_tests_sql = """
    SELECT
        Tests.id,
        TestsTestSets.test_set_id,

        Tests.input,
        Tests.expected_output,
        TestsTestSets.sequence_position
    FROM TestsTestSets
    JOIN Tests
        ON Tests.id = TestsTestSets.test_id
    WHERE
        TestsTestSets.test_set_id = :test_set_id
    """

    def _testFromRow( self, row ):
        return Test(
            id=row[ 0 ],
            input=json.loads( row[ 2 ] ),
            expected_output=json.loads( row[ 3 ] )
        )

    def generate( self ):
        conn = sqlite3.connect( self.sqlite_filename )
        cursor = conn.cursor()

        tests = cursor.execute( SQLTestGenerator.fetch_tests_sql, { 'test_set_id': self.test_set_id } ).fetchall()

        tests = sorted( tests, key=lambda test_row: test_row[ 4 ] )
        tests = map( self._testFromRow, tests )
        tests = list( tests )

        test_set = TestSet( tests, id=self.test_set_id )
 
        conn.close()
        return test_set
