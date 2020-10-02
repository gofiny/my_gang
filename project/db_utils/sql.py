select_user_by_user_id = 'SELECT * FROM users WHERE user_id=$1'


create_users_table = '''CREATE TABLE IF NOT EXISTS users
                    (
                        "uuid" uuid NOT NULL PRIMARY KEY,
                        "user_id" int NOT NULL UNIQUE,
                        "is_followed" bool NOT NULL DEFAULT false
                    )'''

create_new_user = '''INSERT INTO users
                    (
                        "uuid",
                        "user_id"
                    ) VALUES (
                        $1,
                        $2
                    ) RETURNING *'''
