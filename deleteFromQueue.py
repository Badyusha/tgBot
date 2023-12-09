from regToQueue import *

def delete_from_queue(call):
    try:
        connection = sqlite3.connect(r"QueueDatabase.db")
    except Error as e:
        bot.send_message(call.chat.id, 'Невозможно подключиться к БД, пните разрабов')
        help_func(call)
        return
    result = connection.execute('''SELECT LabTable.LabName, LabTable.LabDate, LabTable.GroupNumber
    FROM LabTable
    JOIN Record ON LabTable.ID = Record.LabID
    WHERE Record.UserID = ?''', (call.chat.id,))
    labs_list = result.fetchall()

    if len(labs_list) == 0:
        bot.send_message(call.chat.id, 'Ты шото попутал' ) # no records found
        return
    bot.send_message(call.chat.id, 'Откуда удаляться будем?')
    
    subject_info = """
| № |   Лаба   | Дата лабы | Подгруппа |
========================================
"""

    bot.send_message(call.chat.id, "Введите номер лабы с которой хотите удалиться")

    for i in range(len(labs_list)):
        subject_info += f"|{i + 1: ^{3}}| {labs_list[i][0]: ^{9}}| {labs_list[i][1]: ^{10}}| {labs_list[i][2]: ^{10}}|\n"
    bot.send_message(call.chat.id, '<pre>' + subject_info + '</pre>', parse_mode='html')
    bot.register_next_step_handler(call, process_user_input)


def process_user_input(message):
    try:
        connection = sqlite3.connect(r"QueueDatabase.db")
    except Error as e:
        bot.send_message(message.chat.id, 'Невозможно подключиться к БД, пните разрабов')
        return

    try:
        user_input = int(message.text)
        result = connection.execute('''SELECT ID
        FROM Record
        WHERE Record.UserID = ?''', (message.chat.id,))

        labs_list = result.fetchall()
        if 1 <= user_input <= len(labs_list):
            try:
                delete_query = '''
                DELETE FROM Record
                WHERE UserID = ? AND ID = ?;
                '''
                connection.execute(delete_query, (message.chat.id, labs_list[user_input - 1][0]))
                connection.commit()
                bot.send_message(message.chat.id, f"Вы успешно удалены из очереди на лабу {user_input}.")
            except Error as e:
                bot.send_message(message.chat.id, 'Ошибка при удалении из базы данных.')
        else:
            bot.send_message(message.chat.id, "Введите корректный номер лабы.")
    except ValueError:
        bot.send_message(message.chat.id, "Введите целое число.")
    finally:
        connection.close()
