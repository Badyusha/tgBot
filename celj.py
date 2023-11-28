import telebot
from telebot import types
import sqlite3
from sqlite3 import Error
from tabulate import tabulate
from datetime import datetime
import random
import time

bot = telebot.TeleBot('6885948940:AAGD89B0_Wjs3BCkyJ7s-0jXuKn7GCWkMZ8')

surname = ' '
FinishLab = {}  #глобальный словарь для очередей, которые уже сформировались


# здесь обрабатывается любой текст, который введет юзер
@bot.message_handler(content_types=['text'])
def start(message):
    text = message.text

    try:
        connection = sqlite3.connect(r"QueueDatabase.db")
    except Error as e:
        bot.send_message(message.from_user.id, 'Невозможно подключиться к БД, пните разрабов')
        return

    result = connection.execute(f'select ID from UserTable where ID = {message.from_user.id};')
    connection.close

    if result.fetchall().__len__() != 0 and text == '/start':  # if user with this id already exists
        bot.send_message(message.from_user.id, "Вы уже зарегестрированы!")
        bot.register_next_step_handler(message, menu(message))  # redirect to (main) menu
    elif text == '/start':
        bot.send_message(message.from_user.id, "Введите свою фамилию")
        bot.register_next_step_handler(message, get_surname)  # следующий шаг – функция get_surname
    else:
        bot.send_message(message.from_user.id, 'Не пон 🤨')


def get_surname(message):
    surname = message.text

    try:
        connection = sqlite3.connect(r"QueueDatabase.db")
        connection.execute(f"""
            insert into UserTable(ID, Surname)
            values({message.from_user.id}, '{surname}');
        """)
        connection.commit()
        connection.close
    except Error as e:
        bot.send_message(message.from_user.id, 'Невозможно подключиться к БД, пните разрабов')
        return

    bot.send_message(message.from_user.id, "Вы успешно зарегестрированы!")


def menu(message):
    keyboard = types.InlineKeyboardMarkup();  # наша клавиатура

    on_record_key = types.InlineKeyboardButton(text='Записаться на сдачу', callback_data='on_record')  # кнопка
    keyboard.add(on_record_key)  # добавляем кнопку в клавиатуру

    on_delete_key = types.InlineKeyboardButton(text='Удалиться из очереди', callback_data='on_delete')
    keyboard.add(on_delete_key)

    on_output_key = types.InlineKeyboardButton(text='Вывести список очереди', callback_data='on_output')
    keyboard.add(on_output_key)

    question = 'Вот что вы можете делать со мной:'
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "on_record":
        bot.register_next_step_handler(call.message, register_to_queue(call))

    elif call.data == "on_delete":
        print('тут егор работает')
    elif call.data == "on_output":
        print('тут даша работает')
        bot.register_next_step_handler(call.message, DisplayQueue(call.message))


# Вывод очереди

def DisplayQueue(message):
    current_time = time.strftime("%H:%M", time.localtime())  # текущее время в формате ЧЧ:ММ
    users_info = []  # список юзеров сдающих лабу
    checkLab = {}

    try:
        connection = sqlite3.connect(r"QueueDatabase.db")
    except Error as e:
        bot.send_message(message.chat.id, 'Невозможно подключиться к БД, пните разрабов')
        return

    # считываем данные бд
    users = connection.execute(f'SELECT * FROM UserTable')
    record = connection.execute(f'SELECT * FROM Record')
    result = connection.execute(f'SELECT * FROM LabTable')
    record_lab = record.fetchall()
    users_lab = users.fetchall()
    lab = result.fetchall()

    # создание словаря, где хранятся общие данные по ключу сдаваемой лабы
    record_dict = {}
    dictionaryLab = {}
    for fixation in record_lab:
        recId = fixation[0]
        recUserId = fixation[1]
        recLabId = fixation[2]
        recLabsCount = fixation[3]

        if recLabId in record_dict:  # проверяем, существует ли уже такой ключ в словаре
            record_dict[recLabId].append(
                (recUserId, recLabsCount))  # добавляем значения в существующий список по ключу recLabId
        else:
            record_dict[recLabId] = [(recUserId, recLabsCount)]

    # считывание необходимых данных про лабы и вывод

    for recLabId, values in record_dict.items():  # просмотр словаря с лабами
        for lr in lab:
            lab_id = lr[0]
            lab_name = lr[1]
            group_number = lr[2]
            lab_date = lr[3]
            lab_time = lr[4]
            if lab_time < current_time:
                if recLabId == lab_id:  # считываение данных о лабе по ID
                    for recUserId, recLabsCount in values:
                        lab_info = f"{lab_name}\t Группа: {group_number}\tДата: {lab_date}"

                        # считываение данных о юзерах по ID
                        for us in users_lab:
                            UsId = us[0]
                            UsSurname = us[1]
                            if recUserId == UsId:
                                users_info.append(UsSurname)  # + фамилия в список

                    #проверка есть ли данная очередь в глобал.словаре
                    if (lab_name, group_number, lab_date, lab_time) in FinishLab:
                        users_list = FinishLab[(lab_name, group_number, lab_date, lab_time)]
                    else:
                        # рандомное распредедение
                        unique_users_info = list(set(users_info))  # Убираем повторения
                        random.shuffle(unique_users_info)  # Перемешиваем
                        users_list = "\n".join([f"{i + 1}. {surname}" for i, surname in enumerate(unique_users_info)])
                        FinishLab[(lab_name, group_number, lab_date, lab_time)] = [(users_list)]
                        users_list = []
                        users_info = []
                    # вывод
                    if lab_info is not None:
                        key = (lab_name, group_number, lab_date, lab_time)
                        lab_info = f'{lab_name}  Группа: {group_number}\t Дата: {lab_date}'
                        users_list = '\n'.join([f'{i + 1}. {user}' for i, user in enumerate(FinishLab[key])])[3:]
                        # Отправляем сообщение
                        bot.send_message(chat_id="-4036713338", text=lab_info + '\n' + users_list)

            else:
                key = (lab_name, group_number, lab_date)
                if key in checkLab:
                    break
                else:
                    checkLab[key] = group_number
                    message = f"Запись еще не окончена.\n{lab_name}\tГруппа: {group_number}\t {lab_date}"
                    bot.send_message(chat_id="-4036713338", text=message)


def register_to_queue(call):
    bot.send_message(call.message.chat.id, 'Выберите предмет:')

    try:
        connection = sqlite3.connect(r"QueueDatabase.db")
    except Error as e:
        bot.send_message(call.message.chat.id, 'Невозможно подключиться к БД, пните разрабов')
        return

    result = connection.execute(f'select * from LabTable;')
    labs_list = result.fetchall()

    subject_info = """
| ID | Название предмета | Подгруппа |
===================================
"""

    for i in range(len(labs_list)):
        subject_info += f"| {labs_list[i][0]: <{3}}"
        subject_info += f"| {labs_list[i][1]: <{30}}|"
        subject_info += f" {labs_list[i][2]: ^{10}}|\n"
        # print(subject_info)
    bot.send_message(call.message.chat.id, subject_info)


bot.polling(none_stop=True, interval=0)
