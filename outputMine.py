from deleteFromQueue import *


def display_queue(call):
    try:
        connection = sqlite3.connect(r"QueueDatabase.db")
    except Error as e:
        bot.send_message(call.chat.id, 'Невозможно подключиться к БД, пните разрабов')
        return
    
    record_data = connection.execute(f'select * from Record;')
    records_list = record_data.fetchall()

    if len(records_list) == 0:
        bot.send_message(call.chat.id, "Никто не хочет сдавать лабы(\nСписок пустой")
        return

    labs_data = connection.execute(f'select * from LabTable;')
    labs_list = labs_data.fetchall()

    for lab in labs_list:
        current_time = (int)(time.strftime("%H%M", time.localtime()))

        current_users_lab_count = connection.execute(f'select * from Record where LabID = {lab[0]}').fetchall()

        if (int)(lab[4].replace(':', '')) > current_time:
            text = f'Запись для\n{lab[1]} ---Группа: {lab[2]} --- {lab[3]}\nеще не окончена\n\nСейчас записано: {len(current_users_lab_count)} чел.'
            bot.send_message(call.chat.id, text)
            continue

        dictionary_key = lab[1] + (str)(lab[2]) # lab name and group number is a key

        global randomed_dict
        try:
            randomed_dict[dictionary_key]
        except:
            users_data = connection.execute(f'''select UserTable.Surname, Record.LabsCount, LabTable.LabName, LabTable.GroupNumber 
                                                from Record 
                                                join Labtable on Record.LabID = Labtable.ID
                                                join UserTable on Record.UserID = UserTable.ID
                                                Where  Labtable.ID = {lab[0]};''')
            randomed_dict[dictionary_key] = users_data.fetchall()

            random.shuffle(randomed_dict[dictionary_key])

        show_randomed_users_queue(call, randomed_dict[dictionary_key])
    
    connection.close()


def show_randomed_users_queue(call, queue):
    users_queue = """| № |   Фамилия   | Лаба  | Подгр. | К-во |
===========================================
"""

    for counter in range(len(queue)):
        users_queue += f"|{(str)(counter + 1):^{3}}" # place
        users_queue += f"|{queue[counter][0]: ^{13}}" # name
        users_queue += f"|{queue[counter][2]: ^{7}}" # subject
        users_queue += f"|{queue[counter][3]: ^{8}}" # group
        users_queue += f"|{queue[counter][1]: ^{6}}|\n" # labs count
    bot.send_message(call.chat.id, '<pre>' + users_queue + '</pre>', parse_mode='html')
