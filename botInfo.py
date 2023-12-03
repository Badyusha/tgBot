import telebot
from telebot import types
import sqlite3
from sqlite3 import Error
import random
import time

bot = telebot.TeleBot('6708440193:AAHwhUWSbhwvtKwnU6kHkM8cpNEGfjoyvSQ')
randomed_dict = dict()

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
def help_func(call):

    bot.send_message(call.chat.id,
                     """Что я могу:
/help - выведется это сообщение
/start - только, чтобы зарегаться
/menu - перейти в главное меню
                     """, parse_mode='html')


def menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('Записаться на сдачу')
    item2 = types.KeyboardButton('Удалиться из очереди')
    item3 = types.KeyboardButton('Вывести список очереди')

    markup.add(item1)
    markup.add(item2)
    markup.add(item3)

    bot.send_message(message.chat.id, '<b>Hello! And welcome to the Los Pollos Hermanos family!\nMy name is Gustavo but u can call me SuSq\nWhat do u want?</b>', parse_mode='html', reply_markup=markup)
    

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
