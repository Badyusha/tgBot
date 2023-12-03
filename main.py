from outputMine import *

surname = ' '

@bot.message_handler(content_types=['text'])
def text_handler(call):
    if call.text == 'Записаться на сдачу':
        register_to_queue(call) 
    elif call.text == 'Удалиться из очереди':
        delete_from_queue(call)
    elif call.text == 'Вывести список очереди':
        display_queue(call)


bot.polling(none_stop=True, interval=0)