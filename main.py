from regToQueue import *


surname = ' '


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "on_record":
        register_to_queue(call)

    elif call.data == "on_delete":
        print('тут егор работает')
    else:
        bot.register_next_step_handler(call.message, DisplayQueue(call.message))


bot.polling(none_stop=True, interval=0)