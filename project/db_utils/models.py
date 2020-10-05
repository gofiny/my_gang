class Player:
    def __init__(self, data: dict):
        self.uuid = data.get("uuid")
        self.vk_id = data.get("vk_id")
        self.tlg_id = data.get("tlg_id")
        self.first_name = data.get("first_name")
        self.last_name = data.get("last_name")
        self.name = data.get("name")
        self.health = data.get("health")
        self.power = data.get("power")
        self.first_name = data.get("mind")
        self.respect = data.get("respect")


class Counters:
    def __init__(self, data: dict):
        self.uuid = data.get("uuid")
        self.player = data.get("player")
        self.lm_time = data.get("lm_time")
        self.daily_actions = data.get("daily_actions")
        self.total_actions = data.get("total_actions")


class States:
    def __init__(self, data: dict):
        self.player = data.get("player")
        self.main_state = 0
