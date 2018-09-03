import sqlite3

class MigrationHandler():
    def __init__( self, sqlite_filename, migrations ):
        """
        Pass the full file path to the sqlite file here, since we need to make
        our own connection. Foreign keys don't seem to become active until the
        connection that created them is closed
        """
        self.sqlite_filename = sqlite_filename
        self.migrations = migrations

    create_migration_table_sql = """
    CREATE TABLE MigrationsMeta (
        created_at DATETIME PRIMARY KEY DEFAULT CURRENT_TIMESTAMP,
        migration_level INTEGER NOT NULL
    );
    """

    insert_migration_level_sql = """
    INSERT INTO MigrationsMeta ( migration_level ) VALUES ( ? );
    """

    def migrate( self ):
        conn = sqlite3.connect( self.sqlite_filename )
        cursor = conn.cursor()

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
            cursor.execute( MigrationHandler.create_migration_table_sql )

        for migration_i in range( migration_level, len( self.migrations ) ):
            print( 'Doing migration: ',  migration_i )
            for command in self.migrations[ migration_i ]:
                cursor.execute( command )
            cursor.execute( MigrationHandler.insert_migration_level_sql, ( str( migration_i + 1 ) ) )
            conn.commit()

        conn.commit()
        conn.close()
