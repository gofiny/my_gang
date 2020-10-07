class Counters:
    def __init__(self, player_uuid: str, **kwargs):
        params = {**kwargs}
        self.player = player_uuid
        self.lm_time = params["lm_time"]
        self.daily_actions = params["daily_actions"]
        self.total_actions = params["total_actions"]

    def serialize(self):
        data = {
            "lm_time": self.lm_time,
            "daily_actions": self.daily_actions,
            "total_actions": self.total_actions
        }
        return data


class States:
    def __init__(self, **kwargs):
        params = {**kwargs}
        self.main_state = params["main_state"]

    def serialize(self):
        data = {
            "main_state": self.main_state
        }
        return data


class Player:
    def __init__(self, data: dict):
        self.uuid = data.get("player_uuid")
        self.vk_id = data.get("vk_id")
        self.tlg_id = data.get("tlg_id")
        self.name = data.get("name")
        self.level = data.get("level")
        self.health = data.get("health")
        self.power = data.get("power")
        self.mind = data.get("mind")
        self.respect = data.get("respect")
        self.states = States(**data.get("states"))
        self.counter = Counters(player_uuid=self.uuid, **data.get("counters"))

    def serialize(self):
        data = {
            "uuid": self.uuid,
            "vk_id": self.vk_id,
            "tlg_id": self.tlg_id,
            "name": self.name,
            "level": self.level,
            "health": self.health,
            "power": self.power,
            "mind": self.mind,
            "respect": self.respect,
            "states": self.states.serialize(),
            "counter": self.counter.serialize()
        }
        return data
