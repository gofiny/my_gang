select_pl_uuid_by_user_id = 'SELECT uuid FROM players WHERE %s_id=$1'

select_player_and_stuff = '''SELECT pl.uuid as player_uuid,
                                pl.vk_id, pl.tlg_id, pl.name, pl.health,
                                pl.power, pl.mind, pl.respect, pl.level,
                                co.*
                             FROM players pl
                             LEFT JOIN counters co ON pl.uuid=co.player
                             WHERE pl.uuid=$1'''

create_players_table = '''CREATE TABLE IF NOT EXISTS players
                    (
                        "uuid" uuid NOT NULL PRIMARY KEY,
                        "vk_id" int NULL UNIQUE,
                        "tlg_id" int NULL UNIQUE,
                        "name" varchar(35) NULL,
                        "level" int NOT NULL DEFAULT 1,
                        "health" int NOT NULL DEFAULT 1000,
                        "power" int NOT NULL DEFAULT 100,
                        "mind" int NOT NULL DEFAULT 100,
                        "respect" int NOT NULL DEFAULT 0
                    )'''

create_counters_table = '''CREATE TABLE IF NOT EXISTS counters
                        (
                            "uuid" uuid NOT NULL PRIMARY KEY,
                            "player" uuid NOT NULL REFERENCES "players" ("uuid") ON DELETE CASCADE,
                            "lm_time" int NULL,
                            "daily_actions" int DEFAULT 1,
                            "total_actions" int DEFAULT 1
                        )'''

create_storage_table = '''CREATE TABLE IF NOT EXISTS storage
                          (
                            "uuid" uuid NOT NULL PRIMARY KEY,
                            "player" uuid NOT NULL REFERENCES "player" ("uuid") ON DELETE CASCADE,
                            "watch" int NULL DEFAULT 0,
                            "phone" int NULL DEFAULT 0,
                            "headphones" int NULL DEFAULT 0,
                            "credit_card" int NULL DEFAULT 0,
                            "glasses" int NULL DEFAULT 0,
                            "cap" int NULL DEFAULT 0,
                            "gloves" int NULL DEFAULT 0
                          ('''

create_wallets_table = '''CREATE TABLE IF NOT EXISTS wallets
                          (
                             "uuid" uuid NOT NULL PRIMARY KEY,
                             "player" uuid NOT NULL REFERENCES "players" ("uuid") ON DELETE CASCADE,
                             "dollars" int NOT NULL DEFAULT 300
                          )'''

create_new_player = '''INSERT INTO players
                    (
                        "uuid",
                        "vk_id",
                        "tlf_id",
                        "name",
                        "level",
                        "health",
                        "power",
                        "mind",
                        "respect"
                    ) VALUES ($1,$2, $3, $4, $5, $6, $7, $8, $9, $10, $11) RETURNING *'''

create_new_player_with_stuff = '''WITH player as (
                                    INSERT INTO players
                                    (
                                        uuid, %s_id
                                    ) VALUES ($1, $2) RETURNING uuid), 
                                  wallet as (
                                    INSERT INTO wallets
                                    (
                                        uuid, player
                                    ) VALUES ($3, $1)),
                                  counter as (
                                    INSERT INTO counters
                                    (
                                        uuid, player, lm_time
                                    ) VALUES ($4, $1, $5),
                                  stuff as (
                                    INSERT INTO storage
                                    (
                                        uuid, player
                                    ) VALUES ($6, $1)
                                  ))
                                  SELECT uuid FROM player'''


select_name_from_players = '''SELECT name FROM players WHERE name=$1'''

set_name_to_player = '''UPDATE players SET name=$1 WHERE uuid=$2'''

update_player = '''WITH players as (
                   UPDATE players SET 
                        level=$1,
                        health=$2,
                        power=$3,
                        mind=$4,
                        respect=$5
                    WHERE uuid=$6), 
                    UPDATE counters SET
                        lm_time=$7,
                        daily_actions=$8,
                        total_actions=$9
                    WHERE player=$6'''

check_seller = '''SELECT uuid FROM players WHERE name="seller"'''

create_seller = '''WITH seller AS (
                    INSERT INTO players
                    (
                        uuid, name
                    ) VALUES (
                        $1, "seller"
                    )
                    INSERT INTO storage 
                    (
                        uuid,
                        player,
                        watch,
                        phone,
                        headphones,
                        credit_card,
                        glasses,
                        cap,
                        gloves
                    ) VALUES ($2, $1, 100, 100, 100, 100, 100, 100, 100)'''
