from deleteFromQueue import *

FinishLab = {}

def DisplayQueue(message):
    current_time = (int)(time.strftime("%H%M", time.localtime()))
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

        # in lab_data all from LabTable
        for lab_info in lab_data:
            send_time = (int)(lab_info[4].replace(':', ''))
            if send_time < current_time:
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
                #print(lab_info_formatted + '\n' + queue_list_formatted)
                bot.send_message(chat_id=message.chat.id, text=lab_info_formatted + '\n' + queue_list_formatted)
            elif send_time >= current_time:
                key = (lab_info[1], lab_info[2], lab_info[3])
                if key not in checkLab:
                    checkLab[key] = None
                    text = f"Запись еще не окончена.\n{lab_info[1]}\tГруппа: {lab_info[2]}\t {lab_info[3]}"
                    bot.send_message(chat_id=message.chat.id, text=text)
    cursor.close()
    conn.close()