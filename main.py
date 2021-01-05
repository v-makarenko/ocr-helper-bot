from typing import Dict, Any, List

import telebot, datetime
from telebot.types import CallbackQuery


class RiskyObject:
    name: str
    last_checked: datetime.date

    def __init__(self, name, last_checked=datetime.datetime.min):
        self.name = name
        self.last_checked = last_checked


ACTION_ADD = 'Добавить'
ACTION_DELETE = 'Удалить'
ACTION_DO = 'Отметить действие'
ACTION_LIST = 'Проверить'
ACTION_INIT_FILL = 'Создай'
ACTION_NO_INIT_FILL = 'Не надо, сам создам'
ACTION_BACK = 'Назад'
ACTION_MENU = 'Меню'

bot = telebot.TeleBot('1492966650:AAE8kbS_X662fK0XEAgazR-vrSRd7sdFEwU')
objects_map: Dict[int, List[RiskyObject]] = {}

keyboardMain = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboardMain.row(ACTION_DO, ACTION_LIST)
keyboardMain.row(ACTION_ADD, ACTION_DELETE)

keyboardStart = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboardStart.row(ACTION_INIT_FILL, ACTION_NO_INIT_FILL)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, я помогу тебе не волноваться об утюге, плите или незакрытой двери - '
                                      'просто отметь все перед выходом. Можешь даже сфотографировать (скоро добавим),'
                                      ' если мне не доверяешь. Для начала надо добавить объекты или действия,'
                                      ' которые тебя регулярно тревожат. Я могу помочь и создать три самых популярных -'
                                      ' выключить утюг, выключить плиту, закрыть дверь', reply_markup=keyboardStart)


@bot.message_handler(func=lambda message: message.text == ACTION_INIT_FILL)
def on_init_fill_request(message):
    add_item(message.from_user.id, 'Выключить плиту')
    add_item(message.from_user.id, 'Выключить утюг')
    add_item(message.from_user.id, 'Закрыть дверь')
    bot.send_message(message.chat.id, 'Добавил!', reply_markup=keyboardMain)


def on_add_item_request(message):
    add_item(message.from_user.id, message.text)
    bot.send_message(message.chat.id, 'Добавлeно!', reply_markup=keyboardMain)


@bot.message_handler(func=lambda message: message.text == ACTION_ADD)
def on_add_request(message):
    msg = bot.send_message(message.chat.id, 'Введи действие: ')
    bot.register_next_step_handler(msg, on_add_item_request)


@bot.message_handler(func=lambda message: message.text == ACTION_DELETE)
def on_delete_request(message):
    if message.from_user.id in objects_map and len(objects_map[message.from_user.id]) > 0:
        keyboard_actions = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard_actions.row(*[obj.name for obj in objects_map[message.from_user.id]])
        keyboard_actions.row(telebot.types.KeyboardButton(ACTION_BACK))
        bot.send_message(message.chat.id, 'Какое действие хочешь удалить?', reply_markup=keyboard_actions)
    else:
        bot.send_message(message.chat.id, 'А удалять то нечего(',
                         reply_markup=keyboardMain)



@bot.message_handler(func=lambda message: message.text == ACTION_DO)
def on_do_action_request(message):
    if message.from_user.id in objects_map and len(objects_map[message.from_user.id]) > 0:
        keyboard_actions = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard_actions.row(*[obj.name for obj in objects_map[message.from_user.id]])
        keyboard_actions.row(telebot.types.KeyboardButton(ACTION_BACK))
        msg = bot.send_message(message.chat.id, 'Слава, что ты сделал?', reply_markup=keyboard_actions)
        bot.register_next_step_handler(msg, on_do_exact_action_request)
    else:
        bot.send_message(message.chat.id, 'Сначала добавь актвности, за которые ты переживаешь.',
                         reply_markup=keyboardMain)


def on_do_exact_action_request(message):
    refresh_item_time(message.from_user.id, message.text)
    bot.send_message(message.chat.id, 'Отлично!', reply_markup=keyboardMain)


@bot.message_handler(func=lambda message: message.text == ACTION_LIST)
def on_list_request(message):
    if message.from_user.id in objects_map and len(objects_map[message.from_user.id]) > 0:
        for obj in objects_map[message.from_user.id]:
            bot.send_message(message.chat.id,
                             'Действие ' + obj.name + ', совершено в ' + obj.last_checked.strftime(
                                 "%d/%m, %H:%M:%S"))
    else:
        bot.send_message(message.chat.id, 'Пока что ты не за что не переживаешь :D', reply_markup=keyboardMain)


@bot.message_handler(func=lambda message: message.text == ACTION_BACK)
@bot.message_handler(func=lambda message: message.text == ACTION_MENU)
@bot.message_handler(func=lambda message: message.text == ACTION_NO_INIT_FILL)
def on_back_to_menu_request(message):
    bot.send_message(message.chat.id, ACTION_MENU, reply_markup=keyboardMain)


@bot.message_handler(func=lambda message: message.from_user.id in objects_map and message.text in [obj.name for obj in
                                                                                                   objects_map[
                                                                                                       message.from_user.id]])
def on_delete_item_request(message):
    stored_obj: RiskyObject = [obj for obj in objects_map[message.from_user.id] if obj.name == message.text][0]
    objects_map[message.from_user.id].remove(stored_obj)
    bot.send_message(message.chat.id, 'Удалено!', reply_markup=keyboardMain)


def add_item(user_id, item_name):
    if user_id not in objects_map:
        objects_map[user_id] = []

    objects_map[user_id].append(RiskyObject(item_name, datetime.datetime.min))


def refresh_item_time(user_id, item_name):
    stored_obj: RiskyObject = [obj for obj in objects_map[user_id] if obj.name == item_name][0]
    stored_obj.last_checked = datetime.datetime.now()


bot.polling()
