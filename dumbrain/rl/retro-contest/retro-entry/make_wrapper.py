def make( game, **kwargs ):
    try:
        import gym_remote.client as grc
        return grc.RemoteEnv( 'tmp/sock' )
    except:
        pass
    try:
        from retro_contest.local import make
        return make( game, **kwargs )
    except:
        pass
    raise Exception( 'Unable to make' )
