import telebot
from telebot import types
import sqlite3
from sqlite3 import Error

bot = telebot.TeleBot('6885948940:AAGD89B0_Wjs3BCkyJ7s-0jXuKn7GCWkMZ8')

# здесь обрабатывается /start
@bot.message_handler(commands=['start'])
def start(message):
    try:
        connection = sqlite3.connect(r"QueueDatabase.db")
    except Error as e:
        bot.send_message(message.from_user.id, 'Невозможно подключиться к БД, пните разрабов')
        return
    
    
    result = connection.execute(f'select ID from UserTable where ID = { message.from_user.id };')
    connection.close

    if (result.fetchall().__len__() != 0): # if user with this id already exists 
        bot.send_message(message.from_user.id, "Вы уже зареганы!")
        help_func(message) # redirect to (help menu
        return
    bot.send_message(message.from_user.id, "Введите свою фамилию")
    bot.register_next_step_handler(message, get_surname) #следующий шаг – функция get_surname


@bot.message_handler(commands=['menu'])
def main_menu(message):
    try:
        connection = sqlite3.connect(r"QueueDatabase.db")
    except Error as e:
        bot.send_message(message.from_user.id, 'Невозможно подключиться к БД, пните разрабов')
        return
    
    result = connection.execute(f'select ID from UserTable where ID = { message.from_user.id };')
    connection.close

    if (result.fetchall().__len__() == 0): # if user with this id doesnt exist 
        start(message) # redirect to (main) menu
        return
    menu(message)


@bot.message_handler(commands=['help'])
def help_func(message):
    bot.send_message(message.from_user.id, 
                     """Что я могу:
/help - выведется это сообщение
/start - только, чтобы зарегаться
/menu - перейти в главное меню
                     """)

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
