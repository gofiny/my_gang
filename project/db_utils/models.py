import json
from typing import Union


class Counters:
    def __init__(self, player_uuid: str, **kwargs):
        params = {**kwargs}
        self.player = player_uuid
        self.lm_time = params["lm_time"]
        self.daily_actions = params["daily_actions"]
        self.total_actions = params["total_actions"]

    def serialize(self) -> dict:
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

    def serialize(self) -> dict:
        data = {
            "main_state": self.main_state
        }
        return data


class Player:
    def __init__(self, data: Union[dict, str], need_deserialize: bool = False):
        if need_deserialize:
            data = json.loads(data)
        self.uuid = str(data["player_uuid"])
        self.vk_id = data["vk_id"]
        self.tlg_id = data["tlg_id"]
        self.name = data["name"]
        self.level = data["level"]
        self.health = data["health"]
        self.power = data["power"]
        self.mind = data["mind"]
        self.respect = ["respect"]
        self.states = States(**data["states"])
        self.counter = Counters(player_uuid=self.uuid, **data["counters"])

    def serialize(self) -> str:
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
        return json.dumps(data)
