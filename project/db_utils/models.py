class Counters:
    def __init__(self, player_uuid: str, **kwargs):
        params = {**kwargs}
        self.player = player_uuid
        self.lm_time = params["lm_time"]
        self.daily_actions = params["daily_actions"]
        self.total_actions = params["total_actions"]


class States:
    def __init__(self, **kwargs):
        params = {**kwargs}
        self.main_state = params["main_state"]


class Player:
    def __init__(self, data: dict, make_working_stuff: bool = False):
        self.uuid = data.get("player_uuid")
        self.vk_id = data.get("vk_id")
        self.tlg_id = data.get("tlg_id")
        self.first_name = data.get("first_name")
        self.last_name = data.get("last_name")
        self.name = data.get("name")
        self.level = data.get("level")
        self.health = data.get("health")
        self.power = data.get("power")
        self.first_name = data.get("mind")
        self.respect = data.get("respect")
        if make_working_stuff:
            self.states = States(**data.get("states"))
            self.counter = Counters(player_uuid=self.uuid, **data.get("counters"))
