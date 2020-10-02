def select_user_by_user_id(user_id: int):
    sql = f'SELECT * FROM users WHERE user_id = "{user_id}"'
    return sql
