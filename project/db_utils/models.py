class User:
    def __init__(self, data: dict):
        self.user_id = data.get("user_id")
        self.is_followed = data.get("is_followed")
