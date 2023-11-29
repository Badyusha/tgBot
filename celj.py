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
    current_time = time.strftime("%H:%M", time.localtime())
    conn = sqlite3.connect("QueueDatabase.db")
    cursor = conn.cursor()
    checkLab = {}
    # Читаем информацию из бд
    cursor.execute("SELECT * FROM LabTable")
    lab_data = cursor.fetchall()

    cursor.execute("SELECT * FROM UserTable")
    user_data = cursor.fetchall()

    cursor.execute("SELECT * FROM Record")
    record_data = cursor.fetchall()

    # Организовываем данные записей в словарь
    record_dict = {}
    for rec_id, rec_user_id, rec_lab_id, rec_labs_count in record_data:
        if rec_lab_id in record_dict:
            record_dict[rec_lab_id].append((rec_user_id, rec_labs_count))
        else:
            record_dict[rec_lab_id] = [(rec_user_id, rec_labs_count)]

    # Обработка данных лаб
    for lab_id, values in record_dict.items():
        for lab_info in lab_data:
            if lab_id == lab_info[0] and lab_info[4] < current_time:
                users_info = [user_info[1] for rec_user_id, rec_labs_count in values for user_info in user_data if
                              rec_user_id == user_info[0]]
                lab_key = (lab_info[1], lab_info[2], lab_info[3], lab_info[4])

                if lab_key in FinishLab:
                    queue_list = FinishLab[lab_key]
                else:
                    unique_users_info = list(set(users_info))
                    random.shuffle(unique_users_info)
                    queue_list = "\n".join([f"{i + 1}. {surname}" for i, surname in enumerate(unique_users_info)])
                    FinishLab[lab_key] = [queue_list]

                # вывод
                lab_info_formatted = f'{lab_info[1]}  Группа: {lab_info[2]}\t Дата: {lab_info[3]}\t'
                #queue_list_formatted = '\n'.join([f'{i + 1}. {user}' for i, user in enumerate(FinishLab[lab_key])])
                queue_list_formatted = 'n'.join([f'{user}' for user in FinishLab[lab_key]])
                bot.send_message(chat_id=message.chat.id, text=lab_info_formatted + '\n' + queue_list_formatted)
            elif lab_info[4] > current_time:
                key = (lab_info[1], lab_info[2], lab_info[3])
                if key not in checkLab:
                    checkLab[key] = None
                    text = f"Запись еще не окончена.\n{lab_info[1]}\tГруппа: {lab_info[2]}\t {lab_info[3]}"
                    bot.send_message(chat_id=message.chat.id, text=text)
    cursor.close()
    conn.close()


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
