class PlayerNotRegistered(Exception):
    """Raise if player is not registered"""


class DisconnectedPlayer(Exception):
    """Raise if player is not exists on redis base"""
