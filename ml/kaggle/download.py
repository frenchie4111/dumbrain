import subprocess
import os

def download( competition ):
    data_dir = os.path.join( os.getcwd(), 'data' )
    if not os.path.exists( data_dir ):
        os.makedirs( data_dir )
    subprocess.check_output( [ 'kaggle', 'competitions', 'download', '-p', data_dir, '-c', competition ] )
    unzip_all()
    return os.listdir( data_dir )

def unzip_all( data_dir ):
    files = os.listdir( data_dir )
    for file in files:
        if not file.endswith( '.zip' ):
            continue
        print( file )
