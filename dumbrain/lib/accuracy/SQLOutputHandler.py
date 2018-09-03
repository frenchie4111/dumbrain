import sqlite3

from .core import OutputHandler
from dumbrain.lib.migration import MigrationHandler

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

    def handle( self, test_set_result ):
        cursor = self.conn.cursor()
        cursor.execute( SQLOutputHandler.insert_test_set_result_sql, { 'test_set_id': str( test_set_result.test_set.id ), 'results': str( test_set_result.result ) } )

        for test_result in test_set_result.test_results:
            cursor.execute( SQLOutputHandler.insert_test_sql, { 'id': str( test_result.test.id ), 'input': str( test_result.test.input ), 'expected_output': str( test_result.test.expected_output ) } )
            cursor.execute( SQLOutputHandler.insert_test_result_sql, { 'test_id': str( test_result.test.id ), 'test_set_id': str( test_set_result.test_set.id ), 'results': str( test_result.result ) } )

        self.conn.commit()

    migrations = [
        [
    """
    PRAGMA foreign_keys = ON;
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
    CREATE TABLE TestSetResults (
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

        test_set_id VARCHAR( 200 ) NOT NULL,
        results TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE TestResults (
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        test_id VARCHAR( 200 ) NOT NULL,
        test_set_id VARCHAR( 200 ),
        results TEXT NOT NULL,


        FOREIGN KEY( test_id ) REFERENCES Tests( test_id ),
        FOREIGN KEY( test_set_id ) REFERENCES TestSetResults( test_set_id )
    );
    """
        ] 
    ]

    insert_test_sql = """
    INSERT OR IGNORE INTO Tests ( id, input, expected_output )
    VALUES
        ( :id, :input, :expected_output )
    """

    insert_test_set_result_sql = """
    INSERT INTO TestSetResults ( test_set_id, results )
    VALUES
        ( :test_set_id, :results )
    """

    insert_test_result_sql = """
    INSERT INTO TestResults ( test_id, test_set_id, results )
    VALUES
        ( :test_id, :test_set_id, :results )
    """

if __name__ == '__main__':
    SQLOutputHandler( './test.sql' )
