select_user_by_user_id = 'SELECT * FROM users WHERE user_id=$1'

create_players_table = '''CREATE TABLE IF NOT EXISTS players
                    (
                        "uuid" uuid NOT NULL PRIMARY KEY,
                        "vk_id" int NULL UNIQUE,
                        "tlg_id" int NULL UNIQUE,
                        "first_name" varchar(35) NULL,
                        "last_name" varchar(35) NULL,
                        "name" varchar(35) NOT NULL UNIQUE,
                        "health" int NOT NULL DEFAULT 1000,
                        "power" int NOT NULL DEFAULT 100,
                        "mind" int NOT NULL DEFAULT 100,
                        "respect" int NOT NULL DEFAULT 0
                    )'''

create_counters_table = '''CREATE TABLE IF NOT EXISTS players
                        (
                            "uuid" uuid NOT NULL PRIMARY_KEY,
                            "player" uuid NOT NULL REFERENCES "players" ("uuid") ON DELETE CASCADE,
                            "lm_time" float NULL,
                            "daily_actions" int NULL,
                            "total_actions" int NULL
                        )'''

create_new_player = '''INSERT INTO players
                    (
                        "uuid",
                        "vk_id",
                        "tlf_id",
                        "first_name",
                        "last_name",
                        "name",
                        "health",
                        "power",
                        "mind",
                        "respect"
                    ) VALUES ($1,$2, $3, $4, $5, $6, $7, $8, $9, $10) RETURNING *'''

get_player_counter = '''SELECT * FROM counters WHERE uuid=$1'''
