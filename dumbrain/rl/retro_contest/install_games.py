"""
Installs games from url or uploaded zipfile (upload only works on colab)
"""

from dumbrain.lib.download import downloadAndUnzip, uploadColabAndUnzip
import retro.data
import os
import sys
import argparse

def installGamesFromDir( romdir ):
    roms = [ os.path.join( romdir, rom ) for rom in os.listdir( romdir ) ]
    retro.data.merge( *roms, quiet=False )

def colabInstallGames( romdir='data/roms/' ):
    uploadColabAndUnzip( romdir )
    installGamesFromDir( romdir )

def main():
    parser = argparse.ArgumentParser( description='Installs retro games' )

    parser.add_argument( 'download_url', type=str, default=None, nargs='?', help='Download url for zip file' )
    parser.add_argument( '--romdir', type=str, default='data/roms/', help='Location to store the unzip roms' )

    args = parser.parse_args()

    print( args )

    if args.download_url:
        downloadAndUnzip( args.download_url, args.romdir )
    else:
        raise RuntimeError( 'No .zip file method specified' )

    installGamesFromDir( args.romdir )

if __name__ == '__main__':
    main()
