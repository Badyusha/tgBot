from mypart import *

surname = ' '


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "on_record":
        register_to_queue(call)

    elif call.data == "on_delete":
        delete_from_queue(call)
    else:
        print('тут даша работает')


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
        print(subject_info)
    bot.send_message(call.message.chat.id, subject_info)


def delete_from_queue(call):
    bot.send_message(call.message.chat.id, 'Откуда удаляться будем? :')
    try:
        connection = sqlite3.connect(r"QueueDatabase.db")
    except Error as e:
        bot.send_message(call.message.chat.id, 'Невозможно подключиться к БД, пните разрабов')
        return
    result = connection.execute('''SELECT LabTable.LabName, LabTable.LabDate
    FROM LabTable
    JOIN Record ON LabTable.ID = Record.LabID
    WHERE Record.UserID = ?''', (call.message.chat.id,))
    labs_list = result.fetchall()
    subject_info = """
| № |  Название предмета  |  Дата лабы  |
===================================
"""
    for i in range(len(labs_list)):
        subject_info += f"| {i + 1: ^{3}}| {labs_list[i][0]: ^{36}}| {labs_list[i][1]: ^{10 * 2}}|\n"
    subject_info += "Введите номер лабы с которой хотите удалиться\n"
    bot.send_message(call.message.chat.id, subject_info)
    bot.register_next_step_handler(call.message, process_user_input)


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
    menu(message)


bot.polling(none_stop=True, interval=0)
