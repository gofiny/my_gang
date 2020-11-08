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
power_active_start = '''Тут будет описание прокачки'''
power_active_up = '''Жмиии!!!'''
power_active_down = '''Опускай! \U0001F501 Повторения: %s/10'''
power_active_stuff = '''Воу-воу братишка, ты походу переутомился! \n\U0001F4AA Сила -5'''
power_active_too_much = '''Ты пошел на лишнее повторение и уронил штангу на грудь. \n\U00002764 Здоровье -5'''
power_active_stop = '''Закончил упражнение. \n\U0001F4AA Сила +%s'''
power_lets_finish = '''Ставь штангу! \U0001F501 Повторения: 10/10'''
health_active_start = '''тут будет описание'''
health_active_choose_way = '''будет картинка %s  \U0001F501 Дистанция: %s/2000м'''
health_active_stop = '''Ты закончил бегать \U00002764 Здоровье +%s'''
health_active_too_much = '''Ты переутомился, и упал в обморок. \n\U00002764 Здоровье -5'''
health_lets_finish = '''Заканчивай бегать! %s . \U0001F501 Дистанция: %s/2000м'''
health_fail_way = '''Ты завернул не туда. Тебя пнули под очко и твоя тренировка закончилась. \n\U00002764 Здоровье -5'''
touch_buttons = '''Жми на кнопки'''
action_is_blocked = '''\U00002757 Ты не можешь сейчас этого сделать. Осталось: %s'''
fight_menu = '''Тут Будет что то написано'''
start_search_fight = '''Ищем терпилу для зарубы...'''
scared = '''Засал? Ну ладно...'''
start_fight_you = '''Ты нарвался на %s, у него %s \U00002764\nВыбирай куда будешь бить:'''
choice_hit = '''\nВыбирай куда будешь бить:'''
start_fight_enemy = '''Ты нарвался на %s, у него %s \U00002764\nВыбирай что будешь защищать:'''
choice_guard = '''\nВыбирай что будешь защищать:'''
enemy_give_up = '''Терпила убежал с драки!'''
you_give_up = '''Ты убежал с драки как сыкливая девочка'''
you_success_hit = '''Ты ударил в %s и нанес %s урона\nТы: %s/%s\U00002764\n%s: %s/%s\U00002764'''
you_lose_hit = '''Ты ударил в %s и попал в блок. Нанес %s урона\nТы: %s/%s\U00002764\n%s: %s/%s\U00002764'''
enemy_success_hit = '''Тебя ударили в %s, получено %s урона\nТы: %s/%s\U00002764\n%s: %s/%s\U00002764'''
enemy_lose_hit = '''Тебя ударили в %s, попал в блок. Получено %s урона\nТы: %s/%s\U00002764\n%s: %s/%s\U00002764'''
wait_the_enemy = '''Ждем чужого хода...'''
you_win_fight = '''Ты вырубил противника'''
you_lose_fight = '''Тебя вырубили'''


def storage(player: Player):
    text = '''=== Хранилище ==='''
    for key, value in player.storage.present_stuff.items():
        row = f"\n{key}: {value} шт."
        text += row

    return text


def get_damage_message(is_hit: bool, hit_status: bool, hit_name: str,
                       damage: int, player: Player, enemy: Player) -> str:
    params = (
        hit_name, damage, player.fight_side.health, player.health,
        enemy.name, enemy.fight_side.health, enemy.health
    )
    if is_hit and hit_status:
        return you_success_hit % params
    elif is_hit:
        return you_lose_hit % params
    elif not is_hit and hit_status:
        return enemy_success_hit % params
    else:
        return enemy_lose_hit % params
