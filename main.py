import telebot
from telebot import types
import json

import random
import string

token = open('token.txt').read()
bot = telebot.TeleBot(token)


def queue_drawing(message, queue_id, message_id=False):
    with open('data.json', 'r') as file:
        file_data = dict(json.load(file))
        keyboard = types.InlineKeyboardMarkup()
        keyboard2 = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(text="Приєднатись",
                                             callback_data=f'{queue_id} Приєднатись')
        button2 = types.InlineKeyboardButton(text="Покинути чергу", callback_data=f'{queue_id} Покинути чергу')
        button3 = types.InlineKeyboardButton(text="Оновити чергу", callback_data=f'{queue_id} Оновити чергу')
        button4 = types.InlineKeyboardButton(text="Видалити чергу", callback_data=f'{queue_id} Видалити чергу')

        keyboard.add(button1)
        keyboard2.add(button3, button2)

        if file_data[queue_id]['admin'] == message.chat.id:
            keyboard2.add(button4)

        if not file_data[queue_id]['members']:
            bot.edit_message_text(chat_id=message.chat.id, message_id=message_id,
                                  text='Черга поки-що пуста, додатись у чергу?', reply_markup=keyboard)
            return
    big_message = '\n'.join(
        [f"{num}. {name}\n" for num, name in enumerate(file_data[queue_id]['members'], 1)])
    big_message = f'Черга <b>«{file_data[queue_id]["name"]}»</b>\n\n' + big_message

    new_message = ''
    el_is_at = False
    for el in big_message:
        if el == '@':
            el_is_at = True
            new_message += '@'
            continue
        if el_is_at and el.isdigit():
            new_message += '*'
        else:
            new_message += el
            el_is_at = False
    big_message = new_message

    if message.chat.username:
        username = message.chat.username
    else:
        username = str(message.chat.id)
    for name in file_data[queue_id]['members']:
        if username in name:
            if message_id:
                try:
                    bot.edit_message_text(chat_id=message.chat.id, message_id=message_id, text=big_message,
                                          reply_markup=keyboard2, parse_mode='HTML')
                except:
                    pass
                return
            # bot.send_message(message.chat.id, f'Черга <{file_data[queue_id]["name"]}>:')
            bot.send_message(message.chat.id, big_message, reply_markup=keyboard2, parse_mode='HTML')
            return
    try:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message_id, text=big_message, reply_markup=keyboard,
                              parse_mode='HTML')
    except telebot.apihelper.ApiTelegramException:
        bot.send_message(chat_id=message.chat.id, text=big_message, reply_markup=keyboard, parse_mode='HTML')
    # bot.send_message(message.chat.id, 'Додатись у чергу?', reply_markup=keyboard)


@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.from_user.id
    with open('user_ids.txt', 'r') as f:
        user_ids = f.read().splitlines()
    if str(user_id) not in user_ids:
        with open('user_ids.txt', 'a') as f:
            f.write(str(user_id) + '\n')

    user_name = message.from_user.full_name
    with open('user_names.txt', 'r') as f:
        user_names = f.read().splitlines()
    if str(user_name) not in user_names:
        with open('user_names.txt', 'a') as f:
            f.write(str(user_name) + '\n')

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Створити чергу")
    markup.add(btn1)

    if message.text[7:]:
        queue_id = message.text[7:]
        with open('data.json', 'r') as file:
            file_data = dict(json.load(file))
            keyboard = types.InlineKeyboardMarkup()
            keyboard2 = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton(text="Приєднатись",
                                                 callback_data=f'{queue_id} Приєднатись')
            button2 = types.InlineKeyboardButton(text="Покинути чергу", callback_data=f'{queue_id} Покинути чергу')
            keyboard.add(button1)
            keyboard2.add(button2)
            # bot.send_message(message.chat.id, 'Пошук черги..', reply_markup=markup)

            try:
                if not file_data[queue_id]['members']:
                    bot.send_message(chat_id=message.chat.id, text='Черга поки-що пуста. Приєднатись?',
                                     reply_markup=keyboard)
                else:
                    queue_drawing(message, queue_id)
            except KeyError:
                bot.send_message(message.chat.id, 'Сталася прикра помилка. Можливо черги більше не існує🙁')
    else:
        bot.send_message(message.chat.id,
                         text=f"Привіт👋 {message.from_user.first_name}.\nБот працює в тестовому режимі!",
                         reply_markup=markup)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == 'Створити чергу' or message.text == '/new_queue':
        bot.send_message(message.from_user.id, "Назвіть якось вашу чергу, це може бути щось типу <ШІ-14> або"
                                               " <Боже помилуй 123>")
        return
    queue_name = message.text
    queue_admin = message.chat.id
    with open('queue_list.txt', 'r+', encoding='utf-8') as f:
        for line in f:
            if queue_name in line:
                bot.send_message(message.from_user.id, 'Назва вже зайнята, спробуйте іншу')
                return
        f.write(queue_name + '\n')
        bot.send_message(message.from_user.id, 'Чергу створено')
        print(message.from_user.full_name + ' Створив чергу ' + queue_name)

        letters = string.ascii_letters + string.digits
        queue_id = ''.join(random.choice(letters) for _ in range(10))

        test = {
            queue_id: {
                'name': queue_name,
                'admin': queue_admin,
                'members': []
            }
        }

        with open('data.json', 'r') as file:
            file_data = dict(json.load(file))
        file_data[queue_id] = test[queue_id]
        with open('data.json', 'w') as file:
            json.dump(file_data, file, indent=4)
        message_id = bot.send_message(message.from_user.id,
                                      f'посилання на чергу <{queue_name}>: https://t.me/{bot.get_me().username}?start='
                                      f'{queue_id}').message_id
        bot.pin_chat_message(message.chat.id, message_id)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.from_user.id
    if call.from_user.username:
        name = f'{call.from_user.full_name}\n@{call.from_user.username}'
    else:
        name = f'{call.from_user.full_name}\n@{call.from_user.id}'
    queue_id = call.data.split()[0]
    text_on_button = ' '.join(call.data.split()[1:])
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text="Оновити", callback_data=f'{queue_id} Оновити')
    keyboard.add(button1)
    try:
        if text_on_button == 'Приєднатись':
            with open('data.json', 'r') as file:
                file_data = dict(json.load(file))
                if name not in file_data[queue_id]['members']:
                    file_data[queue_id]['members'].append(name)
                    with open('data.json', 'w') as f:
                        json.dump(file_data, f, indent=4)
                    queue_drawing(message=call.message, queue_id=queue_id,
                                  message_id=call.json['message']['message_id'])
                    print(call.from_user.full_name + ' приєднався до черги ' + file_data[queue_id]['name'])
                    # bot.send_message(chat_id, 'Вітаємо у черзі🥳', reply_markup=keyboard)
        if text_on_button == 'Покинути чергу':
            with open('data.json', 'r') as file:
                file_data = dict(json.load(file))
            if name in file_data[queue_id]['members']:
                file_data[queue_id]['members'].remove(name)
                with open('data.json', 'w') as f:
                    json.dump(file_data, f, indent=4)
                queue_drawing(message=call.message, queue_id=queue_id, message_id=call.json['message']['message_id'])

            # bot.send_message(chat_id, f'Ви покинули чергу🙁', reply_markup=keyboard)
        if text_on_button == 'Оновити чергу':
            queue_drawing(message=call.message, queue_id=queue_id, message_id=call.json['message']['message_id'])

        if text_on_button == 'Видалити чергу':
            keyboard = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton(text="Так",
                                                 callback_data=f'{queue_id} Так')
            button2 = types.InlineKeyboardButton(text="Ні",
                                                 callback_data=f'{queue_id} Ні')
            keyboard.add(button1, button2)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.json['message']['message_id'],
                                  text='<b>Дійсно видалити чергу?</b>', parse_mode='HTML', reply_markup=keyboard)

        if text_on_button == 'Ні':
            queue_drawing(message=call.message, queue_id=queue_id, message_id=call.json['message']['message_id'])

        if text_on_button == 'Так':
            with open('data.json', 'r') as file:
                file_data = dict(json.load(file))
            if queue_id in file_data:
                file_data.pop(queue_id)
                with open('data.json', 'w') as f:
                    json.dump(file_data, f, indent=4)
                if queue_id not in file_data:
                    bot.edit_message_text(chat_id=call.message.chat.id,
                                          message_id=call.json['message']['message_id'],
                                          text='<b>Чергу успішно видалено</b>', parse_mode='HTML')
                else:
                    bot.edit_message_text(chat_id=call.message.chat.id,
                                          message_id=call.json['message']['message_id'],
                                          text='<b>Щось пішло не так🙁</b>', parse_mode='HTML')

    except KeyError:
        bot.send_message(chat_id, 'Сталася прикра помилка. Можливо черги більше не існує🙁')


bot.infinity_polling(none_stop=True, interval=0)
