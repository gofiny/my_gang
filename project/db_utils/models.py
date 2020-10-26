import json
from typing import Union, Optional, Any
from time import time


class EventStuff:
    def __init__(self, data: dict):
        self.info = data.get("info")
        self.upgrade_block = data.get("upgrade_block", 0)

    @property
    def all_stuff(self) -> dict:
        data = {
            "info": self.info,
            "upgrade_block": self.upgrade_block
        }
        return data

    def serialize(self) -> str:
        return json.dumps(self.all_stuff)


class Levels:
    LEVELS = {
        1: {"min": 0, "max": 200},
        2: {"min": 201, "max": 600},
        3: {"min": 601, "max": 1500},
        4: {"min": 1501, "max": 3000},
        5: {"min": 3001, "max": 6000},
        6: {"min": 6001, "max": 10000},
        7: {"min": 10001, "max": 15000},
        8: {"min": 15001, "max": 23000},
        9: {"min": 23001, "max": 33000},
        10: {"min": 33001, "max": 100000}
    }

    def __init__(self, level: int, respect: int):
        self.level = level
        self.respect = respect
        self.current_level = self.LEVELS[self.level]

    def _set_current_level(self):
        self.current_level = self.LEVELS[self.level]

    def _level_up(self) -> None:
        self.level += 1
        self._set_current_level()

    @property
    def how_much_is_left(self) -> int:
        return self.current_level["max"] - (self.respect + 1)

    @property
    def level_max(self) -> int:
        return self.current_level["max"]

    def will_new_level(self) -> bool:
        return self.how_much_is_left <= 0

    def add_respect(self, count: int) -> Optional[int]:
        self.respect += count
        is_new_level = self.will_new_level()
        if is_new_level:
            self._level_up()
            return self.level


class Counters:
    def __init__(self, data: dict):
        self.lm_time = data["lm_time"]
        self.daily_actions = data["daily_actions"]
        self.total_actions = data["total_actions"]

    def plus_one(self):
        self.lm_time = int(time())
        self.daily_actions += 1
        self.total_actions += 1

    @property
    def all_counters(self) -> dict:
        data = {
            "lm_time": self.lm_time,
            "daily_actions": self.daily_actions,
            "total_actions": self.total_actions
        }
        return data

    def serialize(self) -> str:
        self.plus_one()
        return json.dumps(self.all_counters)


class States:
    def __init__(self, data: dict):
        self.main_state = data.get("main_state", 0)
        self.upgrade_state = data.get("upgrade_state", 0)

    @property
    def all_states(self) -> dict:
        states = {
            "main_state": self.main_state,
            "upgrade_state": self.upgrade_state
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
    def present_stuff(self) -> dict:
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

    def serialize(self) -> str:
        return json.dumps(self.data_to_serialize)


class Player:
    def __init__(self, data: Union[dict, str], from_redis: bool = False):
        if from_redis:
            data = json.loads(data)
            self.counters = Counters(data["counters"])
            self.wallet = Wallet(data["wallet"])
            self.storage = Storage(data["storage"])
            self.event_stuff = EventStuff(data["event_stuff"])
        else:
            self.counters = Counters(data)
            self.wallet = Wallet(data)
            self.storage = Storage(data)
            self.event_stuff = EventStuff(data)
        self.uuid = str(data["player_uuid"])
        self.vk_id = data["vk_id"]
        self.tlg_id = data["tlg_id"]
        self.name = data["name"]
        self.health = data["health"]
        self.power = data["power"]
        self.mind = data["mind"]
        self.respect = data["respect"]
        self.level = Levels(level=data["level"], respect=self.respect)
        self.states = States(data.get("states", {}))

    def add_event(self, event_info: Any) -> None:
        self.event_stuff = EventStuff(data={"info": event_info})

    def clear_event_info(self):
        self.event_stuff.info = None

    def add_respect(self, count: int) -> Optional[int]:
        self.respect += count
        new_level = self.level.add_respect(count)
        if new_level:
            self.level = new_level
            return new_level

    @property
    def all_params(self) -> dict:
        data = {
            "player_uuid": self.uuid,
            "vk_id": self.vk_id,
            "tlg_id": self.tlg_id,
            "name": self.name,
            "level": self.level.level,
            "health": self.health,
            "power": self.power,
            "mind": self.mind,
            "respect": self.respect,
            "states": self.states.all_states,
            "counters": self.counters.all_counters,
            "wallet": self.wallet.data_to_serialize,
            "storage": self.storage.data_to_serialize,
            "event_stuff": self.event_stuff.all_stuff
        }
        return data

    def serialize(self) -> str:
        return json.dumps(self.all_params)
