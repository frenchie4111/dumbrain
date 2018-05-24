import lib
import retro.data

romdir = 'data/roms/'

download.downloadAndUnzip( 'http://aiml.mikelyons.org/datasets/sonic/Sonic%20Roms.zip', romdir )
roms = [ os.path.join( romdir, rom ) for rom in os.listdir( romdir ) ]
retro.data.merge(*roms, quiet=False)
