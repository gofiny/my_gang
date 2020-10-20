from db_utils.models import Player


reg_start = '''Эй бедолага, я тебя вижу в первый раз. Назови свою кликуху, если не хочешь чтобы я называл тебя шнырь.'''
req_connect = '''Нажми на кнопку, чтобы подключится'''
welcome = '''Здарова %s. Здесь будет обучение в будущем'''
this_name_taken = '''Бродяга с такой клюкухой уже есть на районе. Придумай свою!'''
name_too_long = '''Воу-воу корешок, давай попроще кликуху себе придумаешь!'''
home = '''Тут будет основное меню'''
my_profile = '''=== %s ===\n\U0001F31F Уровень: %s\n\U0001F91F\
Уважение: %s/%s\n\n\U0001F4AAСила: %s\n\U00002764 Здоровье: %s\n\U0001F9E0 Интеллект: %s'''
wallet = '''=== Кошелек ===\n\U0001F4B5 Доллары: %s$'''
street = '''Выбирай куда будешь двигаться '''
choose_upgrade = '''Выбирать что хочешь прокачать'''


def storage(player: Player):
    text = '''=== Хранилище ==='''
    for key, value in player.storage.present_stuff.items():
        row = f"\n{key}: {value} шт."
        text += row

    return text
