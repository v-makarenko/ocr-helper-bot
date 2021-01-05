from typing import Dict, Any, List

import telebot, datetime
from telebot.types import CallbackQuery


class RiskyObject:
    name: str
    last_checked: datetime.date

    def __init__(self, name, last_checked=datetime.datetime.min):
        self.name = name
        self.last_checked = last_checked


bot = telebot.TeleBot('1492966650:AAE8kbS_X662fK0XEAgazR-vrSRd7sdFEwU')
objects_map: Dict[int, List[RiskyObject]] = {}

keyboardMain = telebot.types.InlineKeyboardMarkup()
keyboardMain.row(telebot.types.InlineKeyboardButton('Добавить', callback_data='cb_add'),
                 telebot.types.InlineKeyboardButton('Удалить', callback_data='cb_delete'),
                 telebot.types.InlineKeyboardButton('Отметить действие', callback_data='cb_do_action'),
                 telebot.types.InlineKeyboardButton('Проверить', callback_data='cb_list'))

keyboardStart = telebot.types.InlineKeyboardMarkup()
keyboardStart.row(
    telebot.types.InlineKeyboardButton('Создай', callback_data='cb_init_fill'),
    telebot.types.InlineKeyboardButton('Не надо, сам создам', callback_data='cb_no_init_fill'))


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, я помогу тебе не волноваться об утюге, плите или незакрытой двери - '
                                      'просто отметь все перед выходом. Можешь даже сфотографировать,'
                                      ' если мне не доверяешь. Для начала надо добавить объекты или действия,'
                                      ' которые тебя регулярно тревожат. Я могу помочь и создать три самых популярных -'
                                      ' выключить утюг, выключить плиту, закрыть дверь', reply_markup=keyboardStart)


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, message.text)


def add_item(user_id, item_name):
    if user_id not in objects_map:
        objects_map[user_id] = []

    objects_map[user_id].append(RiskyObject(item_name, datetime.datetime.min))


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: CallbackQuery):
    if call.data == "cb_add":
        bot.send_message(call.message.chat.id, 'Введи действие: ')

    elif call.data == "cb_delete":
        keyboard_actions = telebot.types.InlineKeyboardMarkup()
        keyboard_actions.row(
            *[telebot.types.InlineKeyboardButton(obj.name, callback_data='cb_del_' + obj.name) for obj in objects_map[call.from_user.id]])
        keyboard_actions.row(telebot.types.InlineKeyboardButton('Назад', callback_data='cb_empty'))
        bot.send_message(call.message.chat.id, 'Какое действие хочешь удалить?', reply_markup=keyboard_actions)
    elif call.data == "cb_list":
        if call.from_user.id in objects_map:
            for obj in objects_map[call.from_user.id]:
                bot.send_message(call.message.chat.id,
                                 'Действие ' + obj.name + ', совершено в ' + obj.last_checked.strftime(
                                     "%d/%m, %H:%M:%S"))
        else:
            bot.send_message(call.message.chat.id, 'Пока что ты не за что не переживаешь :D', reply_markup=keyboardMain)

    elif call.data == "cb_no_init_fill":
        bot.send_message(call.message.chat.id, 'Теперь можешь все добавить!', reply_markup=keyboardMain)
    elif call.data == "cb_init_fill":
        add_item(call.from_user.id, 'Выключить плиту')
        add_item(call.from_user.id, 'Выключить утюг')
        add_item(call.from_user.id, 'Закрыть дверь')
        bot.send_message(call.message.chat.id, 'Добавил!', reply_markup=keyboardMain)
    elif call.data == ("cb_do_action"):
        keyboard_actions = telebot.types.InlineKeyboardMarkup()
        keyboard_actions.row(
            map(lambda obj: telebot.types.InlineKeyboardButton(obj.name, callback_data='cb_act_' + obj.name),
                objects_map[call.from_user.id]))
    elif call.data == ("cb_empty"):
        bot.send_message(call.message.chat.id, 'Главное меню:', reply_markup=keyboardMain)
    elif call.data.startswith("cb_act_"):
        name = call.data[7:]
        stored_obj: RiskyObject = [obj for obj in objects_map[call.from_user.id] if obj.name == name][0]
        stored_obj.date = datetime.datetime.now()
        bot.send_message(call.message.chat.id, 'Главное меню:', reply_markup=keyboardMain)
    elif call.data.startswith("cb_del_"):
        name = call.data[7:]
        stored_obj: RiskyObject = [obj for obj in objects_map[call.from_user.id] if obj.name == name][0]
        objects_map[call.from_user.id].remove(stored_obj)
        bot.send_message(call.message.chat.id, 'Главное меню:', reply_markup=keyboardMain)

    bot.answer_callback_query(call.id)


bot.polling()
