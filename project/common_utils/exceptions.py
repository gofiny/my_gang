class PlayerNotRegistered(Exception):
    """If player is not registered"""


class DisconnectedPlayer(Exception):
    """If player is not exists on redis base"""
    def __init__(self, player_uuid: str, message: str = "Player are not connected"):
        super().__init__(message)
        self.player_uuid = player_uuid


class NameAlreadyExists(Exception):
    """If player name is exists in the database"""


class NotCorrectName(Exception):
    """If player name greater than 30 symbols or lower than 4"""
