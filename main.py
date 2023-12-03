from outputMine import *

surname = ' '

# randomed_dict.clear()

# @bot.callback_query_handler(func=lambda call: True)
# def callback_worker(call):
#     if call.data == "on_record":
#         register_to_queue(call)
#     elif call.data == "on_delete":
#         delete_from_queue(call)
#     else:
#         display_queue(call)

@bot.message_handler(content_types=['text'])
def text_handler(call):
    if call.text == 'Записаться на сдачу':
        register_to_queue(call) 
    elif call.text == 'Удалиться из очереди':
        delete_from_queue(call)
    elif call.text == 'Вывести список очереди':
        display_queue(call)


bot.polling(none_stop=True, interval=0)