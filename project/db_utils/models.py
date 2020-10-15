import json
from typing import Union


class Counters:
    def __init__(self, data: dict):
        self.lm_time = data["lm_time"]
        self.daily_actions = data["daily_actions"]
        self.total_actions = data["total_actions"]

    def serialize(self) -> dict:
        data = {
            "lm_time": self.lm_time,
            "daily_actions": self.daily_actions,
            "total_actions": self.total_actions
        }
        return data


class States:
    def __init__(self, data: dict):
        self.main_state = data["main_state"]

    @property
    def all_states(self) -> dict:
        states = {
            "main_state": self.main_state
        }
        return states

    def serialize(self) -> dict:
        return self.all_states

    def is_that_state(self, state_name: str, value: int) -> bool:
        return self.all_states.get(state_name) == value


class Storage:
    def __init__(self, data: dict):
        self.uuid = data["storage_uuid"]
        self.watch = data["watch"]
        self.phone = data["phone"]
        self.headphones = data["headphones"]
        self.credit_card = data["credit_card"]
        self.glasses = data["glasses"]
        self.cap = data["cap"]
        self.gloves = data["gloves"]

    @property
    def all_stuff(self) -> dict:
        stuff = {
            "watch": self.watch,
            "phone": self.phone,
            "headphones": self.headphones,
            "credit_card": self.credit_card,
            "glasses": self.glasses,
            "cap": self.cap,
            "gloves": self.gloves
        }

        return stuff

    def serialize(self) -> dict:
        return self.all_stuff


class Wallet:
    def __init__(self, data: dict):
        self.uuid = data["wallet_uuid"]
        self.dollars = data["dollars"]

    @property
    def all_currency(self) -> dict:
        currency = {
            "dollars": self.dollars
        }
        return currency

    def serialize(self) -> dict:
        return self.all_currency


class Player:
    def __init__(self, data: Union[dict, str], need_deserialize: bool = False):
        if need_deserialize:
            data = json.loads(data)
            self.states = States(data=data["states"])
            self.counter = Counters(data=data["counters"])
            self.wallet = Wallet(data=data["wallet"])
            self.storage = Storage(data=data["storage"])
        else:
            self.states = data["states"]
            self.counter = data["counters"]
            self.wallet = data["wallet"]
            self.storage = data["storage"]
        self.uuid = str(data["player_uuid"])
        self.vk_id = data["vk_id"]
        self.tlg_id = data["tlg_id"]
        self.name = data["name"]
        self.level = data["level"]
        self.health = data["health"]
        self.power = data["power"]
        self.mind = data["mind"]
        self.respect = data["respect"]

    def serialize(self) -> str:
        data = {
            "player_uuid": self.uuid,
            "vk_id": self.vk_id,
            "tlg_id": self.tlg_id,
            "name": self.name,
            "level": self.level,
            "health": self.health,
            "power": self.power,
            "mind": self.mind,
            "respect": self.respect,
            "states": self.states.serialize(),
            "counters": self.counter.serialize(),
            "wallet": self.wallet.serialize(),
            "storage": self.storage.serialize()
        }
        return json.dumps(data)
