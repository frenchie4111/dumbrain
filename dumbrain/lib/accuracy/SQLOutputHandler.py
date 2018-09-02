import sqlite3

from .core import OutputHandler

create_migration_table_sql = """
CREATE TABLE MigrationsMeta (
    created_at DATETIME PRIMARY KEY DEFAULT CURRENT_TIMESTAMP,
    migration_level INTEGER NOT NULL
);
"""

insert_migration_level_sql = """
INSERT INTO MigrationsMeta ( migration_level ) VALUES ( ? );
"""

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

class SQLOutputHandler( OutputHandler ):
    def __init__( self, sql_filename, initialize=True ):
        self.conn = sqlite3.connect( sql_filename )
        if initialize:
            self.initialize()

    def initialize( self ):
        cursor = self.conn.cursor()

        migration_level = 0

        check_for_migrations_table_sql = """
        SELECT name FROM sqlite_master WHERE type='table' AND name='MigrationsMeta';
        """
        migration_table = cursor.execute( check_for_migrations_table_sql ).fetchone()

        if migration_table is not None:
            get_migration_level_sql = """
            SELECT MAX( migration_level ) AS max FROM MigrationsMeta;
            """
            migration_level_row = cursor.execute( get_migration_level_sql ).fetchone()
            migration_level = migration_level_row[ 0 ]
        else:
            print( 'Initializing migration table' )
            cursor.execute( create_migration_table_sql )

        for migration_i in range( migration_level, len( migrations ) ):
            print( 'Doing migration: ',  migration_i )
            for command in migrations[ migration_i ]:
                cursor.execute( command )
            cursor.execute( insert_migration_level_sql, ( str( migration_i + 1 ) ) )
            self.conn.commit()

        self.conn.commit()

    def handle( self, test_set_result ):
        cursor = self.conn.cursor()
        cursor.execute( insert_test_set_result_sql, { 'test_set_id': str( test_set_result.test_set.id ), 'results': str( test_set_result.result ) } )

        for test_result in test_set_result.test_results:
            cursor.execute( insert_test_sql, { 'id': str( test_result.test.id ), 'input': str( test_result.test.input ), 'expected_output': str( test_result.test.expected_output ) } )
            cursor.execute( insert_test_result_sql, { 'test_id': str( test_result.test.id ), 'test_set_id': str( test_set_result.test_set.id ), 'results': str( test_result.result ) } )

        self.conn.commit()

if __name__ == '__main__':
    SQLOutputHandler( './test.sql' )
