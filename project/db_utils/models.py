import json
from typing import Union


class Counters:
    def __init__(self, data: dict):
        self.lm_time = data["lm_time"]
        self.daily_actions = data["daily_actions"]
        self.total_actions = data["total_actions"]

    @property
    def all_counters(self) -> dict:
        data = {
            "lm_time": self.lm_time,
            "daily_actions": self.daily_actions,
            "total_actions": self.total_actions
        }
        return data

    def serialize(self) -> str:
        return json.dumps(self.all_counters)


class States:
    def __init__(self, data: dict):
        self.main_state = data["main_state"]

    @property
    def all_states(self) -> dict:
        states = {
            "main_state": self.main_state
        }
        return states

    def serialize(self) -> str:
        return json.dumps(self.all_states)

    def is_that_state(self, state_name: str, value: int) -> bool:
        return self.all_states.get(state_name) == value


class Storage:
    def __init__(self, data: dict):
        self.uuid = str(data["storage_uuid"])
        self.watch = data["watch"]
        self.phone = data["phone"]
        self.headphones = data["headphones"]
        self.credit_card = data["credit_card"]
        self.glasses = data["glasses"]
        self.cap = data["cap"]
        self.gloves = data["gloves"]

    @property
    def present_stuff(self):
        stuff = {
            "\U0000231A часы": self.watch,
            "\U0001F4F1 телефоны": self.phone,
            "\U0001F3A7 наушники": self.headphones,
            "\U0001F4B3 кредитки": self.credit_card,
            "\U0001F453 очки": self.glasses,
            "\U0001F9E2 кепки": self.cap,
            "\U0001F9E4 перчатки": self.gloves
        }

        return stuff

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

    @property
    def data_to_serialize(self) -> dict:
        data = self.all_stuff
        data["storage_uuid"] = self.uuid
        return data

    def serialize(self) -> str:
        return json.dumps(self.data_to_serialize)


class Wallet:
    def __init__(self, data: dict):
        self.uuid = str(data["wallet_uuid"])
        self.dollars = data["dollars"]

    @property
    def all_currency(self) -> dict:
        currency = {
            "dollars": self.dollars
        }
        return currency

    @property
    def data_to_serialize(self) -> dict:
        data = self.all_currency
        data["wallet_uuid"] = self.uuid
        return data

    def serialize(self):
        return json.dumps(self.data_to_serialize)


class Player:
    def __init__(self, data: Union[dict, str], from_redis: bool = False):
        if from_redis:
            data = json.loads(data)
            self.counters = Counters(data["counters"])
            self.wallet = Wallet(data["wallet"])
            self.storage = Storage(data["storage"])
        else:
            self.counters = Counters(data)
            self.wallet = Wallet(data)
            self.storage = Storage(data)
        self.uuid = str(data["player_uuid"])
        self.vk_id = data["vk_id"]
        self.tlg_id = data["tlg_id"]
        self.name = data["name"]
        self.level = data["level"]
        self.health = data["health"]
        self.power = data["power"]
        self.mind = data["mind"]
        self.respect = data["respect"]
        self.states = States(data["states"])

    @property
    def all_params(self):
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
            "states": self.states.all_states,
            "counters": self.counters.all_counters,
            "wallet": self.wallet.data_to_serialize,
            "storage": self.storage.data_to_serialize
        }
        return data

    def serialize(self) -> str:
        return json.dumps(self.all_params)
