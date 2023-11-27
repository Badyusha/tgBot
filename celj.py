import telebot
from telebot import types
import sqlite3
from sqlite3 import Error
from tabulate import tabulate
from datetime import date
import random


bot = telebot.TeleBot('6885948940:AAGD89B0_Wjs3BCkyJ7s-0jXuKn7GCWkMZ8')

surname = ' '

# здесь обрабатывается любой текст, который введет юзер
@bot.message_handler(content_types=['text'])
def start(message):
    text = message.text

    try:
        connection = sqlite3.connect(r"QueueDatabase.db")
    except Error as e:
        bot.send_message(message.from_user.id, 'Невозможно подключиться к БД, пните разрабов')
        return
        
    
    result = connection.execute(f'select ID from UserTable where ID = { message.from_user.id };')
    connection.close

    if result.fetchall().__len__() != 0 and text == '/start': # if user with this id already exists 
        bot.send_message(message.from_user.id, "Вы уже зарегестрированы!")
        bot.register_next_step_handler(message, menu(message)) # redirect to (main) menu
    elif text == '/start':
        bot.send_message(message.from_user.id, "Введите свою фамилию")
        bot.register_next_step_handler(message, get_surname) #следующий шаг – функция get_surname
    else:
        bot.send_message(message.from_user.id, 'Не пон 🤨')


def get_surname(message):
    surname = message.text

    try:
        connection = sqlite3.connect(r"QueueDatabase.db")
        connection.execute(f"""
            insert into UserTable(ID, Surname)
            values({ message.from_user.id }, '{surname}');
        """)
        connection.commit()
        connection.close
    except Error as e:
        bot.send_message(message.from_user.id, 'Невозможно подключиться к БД, пните разрабов')
        return

    bot.send_message(message.from_user.id, "Вы успешно зарегестрированы!")


def menu(message):
    keyboard = types.InlineKeyboardMarkup(); #наша клавиатура

    on_record_key = types.InlineKeyboardButton(text='Записаться на сдачу', callback_data='on_record') #кнопка
    keyboard.add(on_record_key) #добавляем кнопку в клавиатуру

    on_delete_key= types.InlineKeyboardButton(text='Удалиться из очереди', callback_data='on_delete')
    keyboard.add(on_delete_key)

    on_output_key= types.InlineKeyboardButton(text='Вывести список очереди', callback_data='on_output')
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




#Вывод очереди
def DisplayQueue(message):
    users_info = [] #список юзеров сдающих лабу

    try:
        connection = sqlite3.connect(r"QueueDatabase.db")
    except Error as e:
        bot.send_message(message.chat.id, 'Невозможно подключиться к БД, пните разрабов')
        return

    current_date = date.today()  # текущая дата
    current_date_str = current_date.strftime("%Y-%m-%d")
    result = connection.execute(f'SELECT * FROM LabTable WHERE LabDate = {}', ) # извлекаем данные, которые совпадают с current_date

    #считываем данные бд
    users = connection.execute(f'SELECT * FROM UserTable')
    record = connection.execute(f'SELECT * FROM Record')
    result = connection.execute(f'SELECT * FROM LabTable')
    record_lab = record.fetchall()
    users_lab = users.fetchall()
    lab = result.fetchall()

    #создание словаря, где хранятся общие данные по ключу сдаваемой лабы
    record_dict = {}
    for fixation in record_lab:
        recId = fixation[0]
        recUserId = fixation[1]
        recLabId = fixation[2]
        recLabsCount = fixation[3]

        if recLabId in record_dict:  # проверяем, существует ли уже такой ключ в словаре
            record_dict[recLabId].append((recUserId, recLabsCount))  # добавляем значения в существующий список по ключу recLabId
        else:
            record_dict[recLabId] = [(recUserId, recLabsCount)]

    for recLabId, values in record_dict.items():  #просмотр словаря с лабами
        for lr in lab:
            lab_id = lr[0]
            lab_name = lr[1]
            group_number = lr[2]
            lab_date = lr[3]

            if recLabId == lab_id: #считываение данных о лабе по ID
                for recUserId, recLabsCount in values:
                    lab_info = f"{lab_name}\t Группа: {group_number}\tДата: {lab_date}"

                    for us in users_lab: #считываение данных о юзерах по ID
                        UsId = us[0]
                        UsSurname = us[1]
                        if recUserId == UsId:
                            users_info.append(UsSurname) # + фамилия в список

                #рандомное распредедение
                unique_users_info = list(set(users_info))  # Убираем повторения
                random.shuffle(unique_users_info)  # Перемешиваем
                users_list = "\n".join([f"{i + 1}. {surname}" for i, surname in enumerate(unique_users_info)])
                #вывод
                if lab_info is not None:
                    bot.send_message(message.chat.id, lab_info + "\n\n" + users_list)



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
        #print(subject_info)
    bot.send_message(call.message.chat.id, subject_info)


bot.polling(none_stop=True, interval=0)


