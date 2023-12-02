from botInfo import *
from datetime import datetime


def register_to_queue(call):
    bot.send_message(call.chat.id, 'Выберите предмет:')

    try:
        connection = sqlite3.connect(r"QueueDatabase.db")
    except Error as e:
        bot.send_message(call.chat.id, 'Невозможно подключиться к БД, пните разрабов')
        help_func(call)
        return

    result = connection.execute(f'select * from LabTable;')
    labs_list = result.fetchall()
    connection.close()


    subject_info = """
| ID  | Название предмета | Подгруппа |
=======================================
"""

    for i in range(len(labs_list)):
        subject_info += f"| {labs_list[i][0]: ^{4}}" # id
        subject_info += f"| {labs_list[i][1]: ^{18}}" # subject
        subject_info += f"| {labs_list[i][2]: ^{9}} |\n" # подгруппа

    bot.send_message(call.chat.id, '<pre>' + subject_info + '</pre>', parse_mode='html')
    bot.register_next_step_handler(call, register_user)


def register_user(message):

    try:
        lab_id = (int)(message.text)
        correct_id(message, lab_id)
    except ValueError:
        bot.send_message(message.from_user.id, "Я устал делать проверки...\nНу давай еще раз")
        bot.register_next_step_handler(message, register_user)
        


def correct_id(message, lab_id):
    try:
        connection = sqlite3.connect(r"QueueDatabase.db")
    except Error as e:
        bot.send_message(message.from_user.id, 'Невозможно подключиться к БД, пните разрабов')
        help_func(message)
        return

    result = connection.execute(f'select * from LabTable where ID = {lab_id};')
    labs_list = result.fetchall()
    connection.close()

    if len(labs_list) == 0:
        bot.send_message(message.from_user.id, "Ты че-то попутал")
        help_func(message)
        return

    record_user(message, lab_id)



def record_user(message, lab_id):
    try:
        connection = sqlite3.connect(r"QueueDatabase.db")
    except Error as e:
        bot.send_message(message.from_user.id, 'Невозможно подключиться к БД, пните разрабов')
        help_func(message)
        return
    
    result = connection.execute(f'select * from Record where UserID = {message.from_user.id} and LabID = {lab_id};')
    records_list = result.fetchall()

    if len(records_list) != 0:
        bot.send_message(message.from_user.id, 'Вы уже записаны в очередь!')
        help_func(message)
        return

    labs_data = connection.execute(f'select * from LabTable;')
    labs_list = labs_data.fetchall()

    if len(labs_list) == 0:
        bot.send_message(message.from_user.id, 'Нет лаб для записи!')
        help_func(message)
        return

    send_time_res = connection.execute(f'select SendTime from LabTable where ID = {lab_id};')
    send_time = send_time_res.fetchall()

    connection.close()

    if (int)(send_time[0][0].replace(':', '')) <= (int)(datetime.now().strftime("%H%M")):
        bot.send_message(message.from_user.id, 'Время записи окончено :(')
        help_func(message)
        return
    
    bot.send_message(message.from_user.id, "Сколько лаб хотите сдать?")
    bot.register_next_step_handler(message, lambda message: check_labs_count(message, lab_id))


def check_labs_count(message, lab_id):
    try:
        labs_count = (int)(message.text)
        if labs_count < 1 or labs_count > 4:
            raise ValueError
        if labs_count == 4:
                bot.send_message(message.from_user.id, "Сомнительно, нооо ОКэЙ")
        record_into_table(message, labs_count, lab_id)
    except ValueError:
        bot.send_message(message.from_user.id, "Не переоценивайте себя!\nДавай еще раз")
        bot.register_next_step_handler(message, lambda message: check_labs_count(message, lab_id))

def record_into_table(message, labs_count, lab_id):
        try:
            connection = sqlite3.connect(r"QueueDatabase.db")
        except Error:
            bot.send_message(message.from_user.id, 'Невозможно подключиться к БД, пните разрабов')
            help_func(message)
            return

        # if someone desides to click on a button 100500 times
        # just erase all records with him and current lab id from the table
        connection.execute(f'delete from Record where UserID = {message.from_user.id} and LabID = {lab_id};')
        connection.commit()

        connection.execute(f'insert into Record(UserId, LabID, LabsCount) values({message.from_user.id},{lab_id},{labs_count});')
        connection.commit()
        connection.close()

        bot.send_message(message.from_user.id, "Вы успешно записаны в очередь!\n")
        help_func(message)
