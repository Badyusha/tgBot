from botInfo import *
from celj import *

lab_id = 0

def register_to_queue(call):
    bot.send_message(call.message.chat.id, 'Выберите предмет:')

    try:
        connection = sqlite3.connect(r"QueueDatabase.db")
    except Error as e:
        bot.send_message(call.message.chat.id, 'Невозможно подключиться к БД, пните разрабов')
        help_func(call.message)
        return

    result = connection.execute(f'select * from LabTable;')
    labs_list = result.fetchall()
    connection.close()


    subject_info = """
| ID  | Подгруппа | Название предмета 
===================================
"""

    for i in range(len(labs_list)):
        subject_info += f"| {labs_list[i][0]: ^{4}}" # id
        subject_info += f"| {labs_list[i][2]: ^{20}}" if (str)(labs_list[i][2]).__len__() == 1 else  f"| {labs_list[i][2]: ^{16}}" # подгруппа
        subject_info += f"| {labs_list[i][1]: <{30}}\n" # subject

    bot.send_message(call.message.chat.id, subject_info)
    bot.register_next_step_handler(call.message, register_user)


def register_user(message):
    try:
        global lab_id
        lab_id = (int)(message.text)
        correct_id(message)
    except ValueError:
        bot.send_message(message.from_user.id, "Я устал делать проверки...\nНу давай еще раз")
        bot.register_next_step_handler(message, register_user)


def correct_id(message):
    try:
        connection = sqlite3.connect(r"QueueDatabase.db")
    except Error as e:
        bot.send_message(message.from_user.id, 'Невозможно подключиться к БД, пните разрабов')
        help_func(message)
        return
    
    result = connection.execute(f'select * from LabTable where ID = {lab_id};')
    labs_list = result.fetchall()
    connection.close()

    if labs_list.__len__() == 0:
        bot.send_message(message.from_user.id, "Ты че-то попутал\nДавай еще раз")
        help_func(message)
        return

    record_user(message)



def record_user(message):
    try:
        connection = sqlite3.connect(r"QueueDatabase.db")
    except Error as e:
        bot.send_message(message.from_user.id, 'Невозможно подключиться к БД, пните разрабов')
        help_func(message)
        return
    
    result = connection.execute(f'select * from Record where UserID = {message.from_user.id} and LabID = {lab_id};')
    records_list = result.fetchall()

    if records_list.__len__() != 0:
        bot.send_message(message.from_user.id, 'Вы уже записаны в очередь!')
        help_func(message)
        return
    
    bot.send_message(message.from_user.id, "Сколько лаб хотите сдать?")
    bot.register_next_step_handler(message, check_labs_count)


def check_labs_count(message):
    try:
        labs_count = (int)(message.text)
        if labs_count < 1 or labs_count > 4:
            raise ValueError
        record_into_table(message)
        

    except ValueError:
        bot.send_message(message.from_user.id, "Не переоценивайте себя!\nДавай еще раз")
        bot.register_next_step_handler(message, check_labs_count)

def record_into_table(message):
    
        try:
            connection = sqlite3.connect(r"QueueDatabase.db")
        except Error as e:
            bot.send_message(message.from_user.id, 'Невозможно подключиться к БД, пните разрабов')
            help_func(message)
            return
        
        connection.execute(f'insert into Record(userId, LabID, LabsCount) values({message.from_user.id},{lab_id},{message.text});')
        connection.commit()
        connection.close()
        bot.send_message(message.from_user.id, "Вы успешно записаны в очередь!\n")
        help_func(message)
