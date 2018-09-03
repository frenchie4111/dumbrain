import sqlite3
import json

from .core import OutputHandler
from dumbrain.lib.migration import MigrationHandler
from .core import TestSetResult, Algorithm

class SQLOutputHandler( OutputHandler ):
    def __init__( self, sql_filename, initialize=True ):
        self.conn = sqlite3.connect( sql_filename )
        self.migration_handler = MigrationHandler( sql_filename, self.getMigrations() )
        if initialize:
            self.initialize()

    def getMigrations( self ):
        return SQLOutputHandler.migrations

    def initialize( self ):
        self.migration_handler.migrate()

    def insertAlgorithmInstance( self, cursor, algorithm ):
        cursor.execute( SQLOutputHandler.insert_algorithm_sql, { 'id': str( algorithm.id ) } )
        cursor.execute( SQLOutputHandler.insert_algorithm_instance_sql, { 
            'algorithm_id': str( algorithm.id ), 
            'description': str( algorithm.description ), 
            'version': str( algorithm.version ), 
            'parameters': json.dumps( algorithm.parameters )
        } )
        return cursor.lastrowid

    def upsert( self, cursor, update_sql, insert_sql, data ):
        cursor.execute( update_sql, data )

        if cursor.rowcount == 0:
            cursor.execute( insert_sql, data )

    def saveTestSet( self, test_set ):
        cursor = self.conn.cursor()

        cursor.execute( SQLOutputHandler.insert_test_set_sql, {
            'id': str( test_set.id )
        } )

        for test_i, test in enumerate( test_set.tests ):
            test_data = {
                'id': str( test.id ),
                'input': json.dumps( test.input ),
                'expected_output': json.dumps( test.expected_output ),
            }

            self.upsert( cursor, SQLOutputHandler.update_test_sql, SQLOutputHandler.insert_test_sql, test_data )

            test_test_set_data = {
                'test_id': str( test.id ),
                'test_set_id': str( test_set.id ),
                'sequence_position': str( test_i )
            }

            self.upsert( cursor, SQLOutputHandler.update_test_test_set_sql, SQLOutputHandler.insert_test_test_set_sql, test_test_set_data )

    def handle( self, test_set_result ):
        self.saveTestSet( test_set_result.test_set )

        cursor = self.conn.cursor()

        algorithm_instance_id = self.insertAlgorithmInstance( cursor, test_set_result.test_set.algorithm )

        cursor.execute( SQLOutputHandler.insert_test_set_result_sql, { 
            'test_set_id': str( test_set_result.test_set.id ), 
            'results': json.dumps( test_set_result.result ),
            'algorithm_instance_id': str( algorithm_instance_id )
        } )

        for test_result_i, test_result in enumerate( test_set_result.test_results ):
            cursor.execute( SQLOutputHandler.insert_test_result_sql, { 
                'test_id': str( test_result.test.id ), 
                'test_set_id': str( test_set_result.test_set.id ), 
                'results': json.dumps( test_result.result ),
                'sequence_position': test_result_i
            } )

        self.conn.commit()

    migrations = [
        [
            """
            PRAGMA foreign_keys = ON;
            """,
            """
            CREATE TABLE TestSets (
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                id VARCHAR( 200 ) PRIMARY KEY
            );
            """,
            """
            CREATE TABLE Tests (
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

                id VARCHAR( 200 ) PRIMARY KEY,

                input TEXT NOT NULL,
                expected_output TEXT NOT NULL
            );
            """,
            """
            CREATE TABLE TestsTestSets (
                test_id VARCHAR( 200 ) NOT NULL,
                test_set_id VARCHAR( 200 ) NOT NULL,
                sequence_position INTEGER NOT NULL,

                PRIMARY KEY( test_set_id, test_id ),
                FOREIGN KEY( test_set_id ) REFERENCES TestSets( id ),
                FOREIGN KEY( test_id ) REFERENCES Tests( test_id )
            )
            """,
            """
            CREATE TABLE Algorithms (
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                id VARCHAR( 200 ) PRIMARY KEY NOT NULL
            );
            """,
            """
            CREATE TABLE AlgorithmInstances (
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                algorithm_id VARCHAR( 200 ) NOT NULL,

                description TEXT NOT NULL,
                version TEXT NOT NULL,
                parameters TEXT NOT NULL,

                FOREIGN KEY( algorithm_id ) REFERENCES Algorithms( id )
            );
            """,
            """
            CREATE TABLE TestSetResults (
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

                test_set_id VARCHAR( 200 ) NOT NULL,
                results TEXT NOT NULL,
                algorithm_instance_id INTEGER NOT NULL,

                FOREIGN KEY( algorithm_instance_id ) REFERENCES AlgorithmInstances( id ),
                FOREIGN KEY( test_set_id ) REFERENCES TestSets( id )
            )
            """,
            """
            CREATE TABLE TestResults (
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                test_id VARCHAR( 200 ) NOT NULL,
                test_set_id VARCHAR( 200 ),
                results TEXT NOT NULL,
                sequence_position INTEGER NOT NULL,

                FOREIGN KEY( test_id ) REFERENCES Tests( test_id ),
                FOREIGN KEY( test_set_id ) REFERENCES TestSetResults( test_set_id )
            );
            """
        ]
    ]

    insert_test_set_sql = """
    INSERT OR IGNORE INTO TestSets ( id )
    VALUES
        ( :id )
    """

    insert_test_sql = """
    INSERT OR IGNORE INTO Tests ( id, input, expected_output )
    VALUES
        ( :id, :input, :expected_output )
    """

    update_test_sql = """
    UPDATE Tests
        SET
            input = :input,
            expected_output = :expected_output
        WHERE
            id = :id
    """

    insert_test_test_set_sql = """
    INSERT OR IGNORE INTO TestsTestSets( test_set_id, test_id, sequence_position )
    VALUES
        ( :test_set_id, :test_id, :sequence_position )
    """

    update_test_test_set_sql = """
    UPDATE TestsTestSets
    SET
        sequence_position = :sequence_position
    WHERE
        test_set_id = :test_set_id AND
        test_id = :test_id;
    """

    insert_algorithm_sql = """
    INSERT OR IGNORE INTO Algorithms ( id )
    VALUES
        ( :id );
    """

    insert_algorithm_instance_sql = """
    INSERT INTO AlgorithmInstances
        ( algorithm_id, description, version, parameters )
    VALUES
        ( :algorithm_id, :description, :version, :parameters );
    """

    insert_test_set_result_sql = """
    INSERT INTO TestSetResults ( test_set_id, results, algorithm_instance_id )
    VALUES
        ( :test_set_id, :results, :algorithm_instance_id )
    """

    insert_test_result_sql = """
    INSERT INTO TestResults ( test_id, test_set_id, results, sequence_position )
    VALUES
        ( :test_id, :test_set_id, :results, :sequence_position )
    """

fetch_test_set_results_sql = """
SELECT * 
FROM TestSetResults 
JOIN AlgorithmInstances 
    ON TestSetResults.algorithm_instance_id = AlgorithmInstances.id
;
"""

def createTestSetResultFromRow( row ):
    """
        TODO: This is brittle as fuck
    """
    test_set_result = TestSetResult( None )
    test_set_result.id = row[ 1 ]
    test_set_result.result = json.loads( row[ 2 ] )
    test_set_result.algorithm_instance_id = row[ 3 ]

    algorithm = Algorithm(
        id=row[ 6 ],
        description=row[ 7 ],
        version=row[ 8 ],
        parameters=json.loads( row[ 9 ] )
    )
    test_set_result.algorithm = algorithm

    return test_set_result

def loadSQLHistory( sqlite_filename ):
    conn = sqlite3.connect( sqlite_filename )

    cursor = conn.cursor()

    test_set_results = cursor.execute( fetch_test_set_results_sql ).fetchall()
    test_set_results = list( map( createTestSetResultFromRow, test_set_results ) )

    conn.close()
    return test_set_results

if __name__ == '__main__':
    SQLOutputHandler( './test.sql' )
